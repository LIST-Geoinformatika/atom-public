
import json
import os

from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.management.base import BaseCommand
from inspire.models import RibolovnaPodzona


class Command(BaseCommand):
    help = """
        Programatically create entries for ribolovne zone
    """

    def handle(self, *args, **options):

        current_dir = os.path.dirname(os.path.abspath(__file__))
        geojson_fpath = os.path.join(current_dir, 'resources', 'ribolovne_podzone.geojson')

        failed = 0
        created_entries = 0
        existing_entries = 0

        with open(geojson_fpath) as f:
            data = json.load(f)

        features = data['features']

        for i, feature in enumerate(features):
            properties = feature['properties']
            coordinates = feature['geometry']['coordinates']

            try:
                polygons = []
                for p in coordinates:
                    polygons.append(Polygon(p[0]))
                geom = MultiPolygon(polygons)
            except Exception:
                failed += 1
                continue

            obj, created = RibolovnaPodzona.objects.get_or_create(
                oznaka=properties['Podzona'],
                geom=geom
            )

            if created:
                created_entries += 1
            else:
                existing_entries += 1

        print("Failed: {}".format(failed))
        print("Created: {}".format(created_entries))
        print("Existing: {}".format(existing_entries))
