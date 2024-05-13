# Register your models here.
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Organization, PasswordResetRequest


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email')
admin.site.register(Organization, OrganizationAdmin)  # noqa


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'organization')}),
        (('Permissions'), {
            'fields': ('is_active', 'email_confirmed', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = (
        'email', 'first_name', 'last_name', 'is_staff',
        'email_confirmed', 'organization', 'language_preference'
    )
    list_filter = ('organization', )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('date_joined',)

admin.site.register(get_user_model(), CustomUserAdmin)  # noqa


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('received_on', 'user', 'uid', 'confirmed')
    list_filter = ('received_on', )
