import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .models import PasswordResetRequest, User
from .permissions import UserPermission
from .serializers import (CustomCookieTokenRefreshSerializer,
                          CustomTokenObtainPairSerializer,
                          PasswordResetConfirmSerializer,
                          PasswordResetSerializer, PasswordChangeSerializer,
                          UserDetailSerializer, UserDetailUpdateSerializer,
                          UserSerializer)
from .utils import Util


def activate(request, uidb64, token):  # TODO: rewrite to CBV

    try:
        user = Util.check_token(uidb64, token)
    except Exception:
        return HttpResponse("Unable to verify your e-mail adress")
    if user is not None:
        user.email_confirmed = True
        user.save()

        if request.user.is_authenticated:
            messages.success(request, "Hvala Vam na potvrdi email adrese.")
            return redirect(settings.FRONTEND_URL)
        else:
            msg = "Hvala Vam na potvrdi email adrese. Sad se možete ulogirati u svoj korisnički račun."
            messages.success(request, msg)
            return redirect(settings.FRONTEND_URL)
    else:
        return HttpResponse('Vaš korisnički račun je već aktiviran ili aktivacijski link nije ispravan.')


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""

    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        if settings.AUTH_EMAIL_VERIFICATION in ["mandatory", "optional"]:
            try:
                self.send_confirmation_email(request, serializer.instance)
            except Exception:
                return Response(
                    _("User was created but server wasn't able to send e-mail!"),
                    status=status.HTTP_202_ACCEPTED
                )

        headers = self.get_success_headers(serializer.data)
        response_msg = {
            "account_created": serializer.data,
            "info": _("Confirmation e-mail was sent to your e-mail address, please confirm it to start using this app!")
        }
        return Response(response_msg, status=status.HTTP_201_CREATED, headers=headers)

    def send_confirmation_email(self, request, user):
        token_data = Util.get_token(user)
        relative_link = reverse('user:activate', kwargs=token_data)
        link = request.build_absolute_uri(relative_link)

        # Variables used in both templates
        template_vars = {
            'email': user.email,
            'link': link,
            'greeting': _("Hi,"),
            'info': _("Please click on the link to confirm your registration!"),
            'description_msg': _("Your e-mail:"),
        }
        text_content = render_to_string('acc_activate_email.txt', template_vars)

        # Adding extra variables to html template
        html_content = render_to_string('acc_activate_email.html', {
            **template_vars,
            'bttn_text': _("Confirm email"),
            'alternate_text': _("Or go to link:")
        })
        data = {
            "body": text_content,
            "to": [user.email],
            "subject": _("Please confirm your e-mail"),
        }
        Util.send_email(html_content, **data)
        return


class CustomObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get(settings.AUTH_REFRESH_TOKEN_NAME):
            # # # Move refresh token from body to HttpOnly cookie

            refresh_token_name = settings.AUTH_REFRESH_TOKEN_NAME
            persist = request.data.get('persist', False)
            max_age = response.data['lifetime'] if persist else None

            response.set_cookie(
                refresh_token_name,
                response.data[refresh_token_name],
                max_age=max_age,
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            # Remove from body
            del response.data[refresh_token_name]
            del response.data["lifetime"]

        return super().finalize_response(request, response, *args, **kwargs)


class CustomCookieTokenRefreshView(TokenRefreshView):
    serializer_class = CustomCookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get(settings.AUTH_REFRESH_TOKEN_NAME):
            # # # Move refresh token from body to HttpOnly cookie

            refresh_token_name = settings.AUTH_REFRESH_TOKEN_NAME
            persist = request.data.get('persist', False)
            max_age = response.data['lifetime'] if persist else None

            response.set_cookie(
                refresh_token_name,
                response.data[refresh_token_name],
                max_age=max_age,
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            # Remove from body
            del response.data[refresh_token_name]
            del response.data["lifetime"]

        return super().finalize_response(request, response, *args, **kwargs)


class LogoutView(APIView):

    renderer_classes = [JSONRenderer]
    permission_classes = []

    @swagger_auto_schema(
        responses={'200': 'OK', '400': 'Bad Request'},
        operation_id='LogoutUser',
        operation_description='Logout user and  clean cookies'
    )
    def post(self, request, *args, **kwargs):

        response = Response()

        response.set_cookie("sessionid", None, max_age=1, httponly=True)  # logout from django admin!
        response.set_cookie(
            settings.AUTH_REFRESH_TOKEN_NAME,
            None,
            max_age=1,
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )

        return response


class RequestUserDetailView(APIView):

    renderer_classes = [JSONRenderer]
    permission_classes = []

    @swagger_auto_schema(
        responses={'200': 'OK', '400': 'Bad Request'},
        operation_id='UserDetail',
        operation_description='Get details for request user'
    )
    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        data = UserDetailSerializer(user).data
        return Response(status=status.HTTP_200_OK, data=data)

    @swagger_auto_schema(
        responses={'200': 'OK', '400': 'Bad Request'},
        operation_id='UserDetailUpdate',
        operation_description='Update details for request user',
        request_body=UserDetailUpdateSerializer
    )
    def put(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        data = self.request.data

        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.language_preference = data.get('language_preference', user.first_name)
        user.save()

        user_data = UserDetailSerializer(user).data
        return Response(status=status.HTTP_200_OK, data=user_data)


class DeleteUserView(generics.DestroyAPIView):
    permission_classes = [UserPermission]
    queryset = User.objects.all()


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = PasswordChangeSerializer

    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.data.get("new_password"))
            user.save()

            response = {'message': 'Password updated successfully'}
            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    """
    Use this endpoint to send email to user with password reset key.
    """

    serializer_class = PasswordResetSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.data.get('email'))
            except User.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            # Build the password reset link
            current_site = get_current_site(self.request)
            domain = current_site.domain
            uid = uuid.uuid4()
            token = default_token_generator.make_token(user)
            reset_link = "https://{domain}/password-reset/{uid}/{token}/".format(domain=domain, uid=uid, token=token)

            # create password reset obj
            PasswordResetRequest.objects.create(user=user, uid=uid, confirmed=False)

            # send e-mail
            subject = "Password reset"
            message = (
                "You're receiving this email because you requested a password reset for your account.\n\n"
                "Please visit this url to set new password:\n{reset_link}".format(reset_link=reset_link)
            )
            from_email = settings.DEFAULT_FROM_EMAIL

            try:
                send_mail(subject, message, from_email, [user.email])
            except BadHeaderError:
                return Response({"error": "Invalid header found."}, status=status.HTTP_400_BAD_REQUEST)

            response = {"message": "E-mail successfully sent."}
            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Use this endpoint to finish reset password process.
    """

    permission_classes = []
    authentication_classes = []

    def get_serializer_class(self):
        return PasswordResetConfirmSerializer

    def post(self, request, **kwargs):
        try:
            uid = uuid.UUID(self.kwargs['uid'])
            obj = PasswordResetRequest.objects.get(uid=uid)
            user = obj.user
        except (ValueError, PasswordResetRequest.DoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'UID is not valid'})

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # check if token is valid
        token_valid = default_token_generator.check_token(obj.user, serializer.data["token"])

        if not token_valid:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Token not valid'})

        # set new password
        user.set_password(serializer.data["new_password"])
        user.save()

        # update object in db
        obj.confirmed = True
        obj.confirmed_on = timezone.now()
        obj.save()

        return Response(status=status.HTTP_200_OK)
