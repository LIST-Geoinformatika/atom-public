from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from user.models import User


class Command(BaseCommand):
    help = """
        Programatically set application permissions and groups\n
        usage: python manage.py create_groups_and_permissions.py
    """

    def handle(self, *args, **options):
        # get or create groups
        admin_group, created = Group.objects.get_or_create(name='Admin')
        editor_group, created = Group.objects.get_or_create(name='Editor')
        viewer_group, created = Group.objects.get_or_create(name='Viewer')

        # define content types
        ct_user = ContentType.objects.get_for_model(User)

        # define permissions
        application_permissions = [
            # (codename, name, content_type, list_of_groups_to_assign_perm)

            ('add_user', 'Can add new users', ct_user, [admin_group]),
            ('change_user', 'Can change existing user', ct_user, [admin_group]),
            ('delete_user', 'Can delete existing user', ct_user, [admin_group]),
            ('add_data', 'Can add new data', ct_user, [admin_group, editor_group]),

            # Example of additional permissions
            # ('change_data', 'Can change data in DB', ct_user, [admin_group, editor_group]),
            # ('delete_data', 'Can delete data in DB', ct_user, [admin_group, editor_group]),
            # ('view_data', 'Can view existing data', ct_user, [admin_group, editor_group, viewer_group])
        ]

        # get or create permissions and add them to appropriate groups
        for permission_tuple in application_permissions:
            permission_obj, created = Permission.objects.get_or_create(
                codename=permission_tuple[0],
                name=permission_tuple[1],
                content_type=permission_tuple[2]
            )

            for group in permission_tuple[3]:
                group.permissions.add(permission_obj)
