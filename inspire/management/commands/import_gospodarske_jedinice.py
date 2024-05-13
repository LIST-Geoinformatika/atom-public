
import json
import os

from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.management.base import BaseCommand
from inspire.models import GospodarskaJedinica


class Command(BaseCommand):
    help = """
        Programatically create entries for gospodarske jedinice
    """

    def handle(self, *args, **options):

        current_dir = os.path.dirname(os.path.abspath(__file__))
        geojson_fpath = os.path.join(current_dir, 'resources', 'gospodarske_jedinice.geojson')

        failed = 0
        created_entries = 0
        existing_entries = 0

        with open(geojson_fpath) as f:
            data = json.load(f)

        features = data['features']

        for i, feature in enumerate(features):
            properties = feature['properties']

            gid = properties.get('gid')
            oznaka = properties.get('gj', '')
            naziv = properties.get('ngj', '')
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
                obj = GospodarskaJedinica.objects.get(gid=gid)
                obj.geom = geom
                obj.oznaka = oznaka
                obj.naziv = naziv
                obj.save()
                created = False
            except GospodarskaJedinica.DoesNotExist:
                obj = GospodarskaJedinica.objects.create(
                    gid=gid,
                    geom=geom,
                    oznaka=oznaka,
                    naziv=naziv
                )
                created = True

            if created:
                created_entries += 1
            else:
                existing_entries += 1

        print("Failed: {}".format(failed))
        print("Created: {}".format(created_entries))
        print("Existing: {}".format(existing_entries))
