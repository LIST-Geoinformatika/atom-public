"""setup URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static

router = DefaultRouter()

api_schema_view = get_schema_view(
    openapi.Info(
        title="API docs",
        default_version="v1",
        description="Swagger docs for ListLabs API",
        contact=openapi.Contact(email="dev@listlabs.net"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/user/", include("user.urls")),
    path("api/webhook/", include("webhook.urls")),
    path("api/inspire/", include("inspire.urls")),
    path("", include(router.urls)),
    path("", include("django_prometheus.urls")),
]

if settings.SHOW_API_DOCS:
    urlpatterns += [
        path(
            "api/docs/swagger/",
            api_schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "api/docs/redoc/",
            api_schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc-ui",
        ),
    ]


if settings.DEBUG:
    urlpatterns += static(settings.DATA_URL, document_root=settings.DATA_DIR)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
