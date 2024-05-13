

from django.urls import path

from webhook import views

urlpatterns = [
    path('alert-manager/', views.AlertManagerWebhook.as_view(), name='alert-manager-webhook'),
]
