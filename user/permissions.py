from django.contrib.auth.models import Group
from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """
    Custom permission to only allow users with permissions
    to view/add/update/delete the users.
    """

    def has_permission(self, request, view):

        # we cover delete permissions in has_object_permissions
        if request.method == 'DELETE':
            return True

        if request.method in permissions.SAFE_METHOD:
            return True

        if not request.user.app_role_id:
            return False

        app_role = Group.objects.get(pk=request.user.app_role_id)
        return 'add_user' in app_role.permissions.all().values_list(
            'codename', flat=True)

    def has_object_permission(self, request, view, obj):

        if request.method == 'DELETE':
            return request.user == obj

        if not request.user.app_role_id:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        app_role = Group.objects.get(pk=request.user.app_role_id)

        permission_dict = {
            'PATCH': 'change_user',
            'PUT': 'change_user'
        }
        perm = permission_dict[request.method]

        return perm in app_role.permissions.all().values_list('codename', flat=True)