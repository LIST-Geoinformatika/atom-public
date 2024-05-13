from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


class Util:
    @staticmethod
    def send_email(html_content, **data):
        try:
            email = EmailMultiAlternatives(**data)
            email.attach_alternative(html_content, "text/html")
            email.send()
        except Exception:
            raise Exception("Sending e-mail went wrong")

    @staticmethod
    def get_token(user):

        try:
            data = {
                "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user)
            }
        except Exception:
            return None
        return data

    @staticmethod
    def check_token(uidb64, token):
        try:
            User = get_user_model()
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Check token
        if user is not None and default_token_generator.check_token(user, token):
            return user
        raise Exception("Token invalid")
