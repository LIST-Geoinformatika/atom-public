
import json
import os

from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.management.base import BaseCommand
from inspire.models import GranicaLovista


class Command(BaseCommand):
    help = """
        Programatically create entries for lovista
    """

    def handle(self, *args, **options):

        current_dir = os.path.dirname(os.path.abspath(__file__))
        geojson_fpath = os.path.join(current_dir, 'resources', 'lovista.geojson')

        failed = 0
        created_entries = 0
        existing_entries = 0

        with open(geojson_fpath) as f:
            data = json.load(f)

        features = data['features']

        for i, feature in enumerate(features):
            properties = feature['properties']

            loviste = properties.get('Lovište')
            status = properties.get('STATUS', '')
            coordinates = feature['geometry']['coordinates']

            try:
                polygons = []
                for p in coordinates:
                    polygons.append(Polygon(p[0]))
                geom = MultiPolygon(polygons)
            except Exception:
                failed += 1
                continue

            try:
                obj = GranicaLovista.objects.get(loviste=loviste)
                obj.geom = geom
                obj.update(geom=geom, status=status)
                created = False
            except GranicaLovista.DoesNotExist:
                obj = GranicaLovista.objects.create(
                    loviste=loviste,
                    geom=geom,
                    status=status
                )
                created = True

            if created:
                created_entries += 1
            else:
                existing_entries += 1

        print("Failed: {}".format(failed))
        print("Created: {}".format(created_entries))
        print("Existing: {}".format(existing_entries))
