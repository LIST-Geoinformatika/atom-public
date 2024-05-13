from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Create or recreate materialized views"

    def handle(self, *args, **options):
        # Drop the public view if it exists
        with connection.cursor() as cursor:
            cursor.execute(
                "DROP MATERIALIZED VIEW IF EXISTS v_odsjeksumasumoposjednika_public"
            )

        # Create the public materialized view
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE MATERIALIZED VIEW v_odsjeksumasumoposjednika_public AS SELECT id, geom FROM \
                    inspire_odsjeksumasumoposjednika"
            )

        self.stdout.write(
            self.style.SUCCESS("Public materialized view created successfully")
        )

        # Drop the private view if it exists
        with connection.cursor() as cursor:
            cursor.execute(
                "DROP MATERIALIZED VIEW IF EXISTS v_odsjeksumasumoposjednika_private"
            )

        # Create the private materialized view
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE MATERIALIZED VIEW v_odsjeksumasumoposjednika_private AS SELECT * FROM \
                    inspire_odsjeksumasumoposjednika"
            )

        self.stdout.write(
            self.style.SUCCESS("Private materialized view created successfully")
        )
