
import json
import os

from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.management.base import BaseCommand

from inspire.models import (Bonitet, GospodarskaJedinica, Izmjera,
                            OdsjekSumaSumoposjednika, UgrozaOdPozara)


class Command(BaseCommand):
    help = """
        Programatically create entries for gospodarske jedinice
    """

    def handle(self, *args, **options):

        current_dir = os.path.dirname(os.path.abspath(__file__))
        geojson_fpath = os.path.join(current_dir, 'resources', 'odsjeci_suma.geojson')

        failed = 0
        created_entries = 0
        existing_entries = 0

        with open(geojson_fpath) as f:
            data = json.load(f)

        features = data['features']

        for i, feature in enumerate(features):
            properties = feature['properties']

            gid = properties.get('gid')
            coordinates = feature['geometry']['coordinates']

            try:
                polygons = []
                for p in coordinates:
                    polygons.append(Polygon(p[0]))
                geom = MultiPolygon(polygons)
            except Exception:
                failed += 1
                continue

            gjid = properties.get('gjid')  # ovo zapravo nije gid od GJ objekta nego oznaka
            try:
                gospodarska_jedinica = GospodarskaJedinica.objects.get(oznaka=gjid)
            except GospodarskaJedinica.DoesNotExist:
                gospodarska_jedinica = None

            veza = properties.get('veza', '')
            godina = properties.get('godina')
            oznaka = properties.get('oznaka', '')
            odjel = properties.get('odjel')
            odsjek = properties.get('odsjek', '')

            ugroza_od_pozara_naziv = properties.get('ugrodpozaranaziv')
            if ugroza_od_pozara_naziv:
                ugroza_od_pozara, _ = UgrozaOdPozara.objects.get_or_create(naziv=ugroza_od_pozara_naziv)
            else:
                ugroza_od_pozara = None

            bonitetnaziv = properties.get('bonitetnaziv')
            if bonitetnaziv:
                bonitet, _ = Bonitet.objects.get_or_create(naziv=bonitetnaziv)
            else:
                bonitet = None

            izmjeranaziv = properties.get('izmjeranaziv')
            if izmjeranaziv:
                izmjera, _ = Izmjera.objects.get_or_create(naziv=izmjeranaziv)
            else:
                izmjera = None

            privlacenje = properties.get('privlacenje', '')
            minophodnja = properties.get('minophodnja', '')
            urid = properties.get('urid', '')
            ur_razred_naziv = properties.get('urrazrednaziv', '')
            prihodi_naziv = properties.get('prihodinaziv', '')
            gospodarski_oblik_naziv = properties.get('gospobliknaziv', '')
            zemljista_naziv = properties.get('zemljistanaziv')

            try:
                obj = OdsjekSumaSumoposjednika.objects.get(gid=gid)
                obj.geom = geom
                obj.gospodarska_jedinica = gospodarska_jedinica
                obj.veza = veza
                obj.godina = godina
                obj.oznaka = oznaka
                obj.odjel = odjel
                obj.odsjek = odsjek
                obj.ugroza_od_pozara = ugroza_od_pozara
                obj.bonitet = bonitet
                obj.izmjera = izmjera
                obj.privlacenje = privlacenje
                obj.minophodnja = minophodnja
                obj.urid = urid
                obj.ur_razred_naziv = ur_razred_naziv
                obj.prihodi_naziv = prihodi_naziv
                obj.gospodarski_oblik_naziv = gospodarski_oblik_naziv
                obj.zemljista_naziv = zemljista_naziv

                obj.save()
                created = False
            except OdsjekSumaSumoposjednika.DoesNotExist:
                obj = OdsjekSumaSumoposjednika.objects.create(
                    gid=gid,
                    geom=geom,
                    gospodarska_jedinica=gospodarska_jedinica,
                    veza=veza,
                    godina=godina,
                    oznaka=oznaka,
                    odjel=odjel,
                    odsjek=odsjek,
                    ugroza_od_pozara=ugroza_od_pozara,
                    bonitet=bonitet,
                    izmjera=izmjera,
                    privlacenje=privlacenje,
                    minophodnja=minophodnja,
                    urid=urid,
                    ur_razred_naziv=ur_razred_naziv,
                    prihodi_naziv=prihodi_naziv,
                    gospodarski_oblik_naziv=gospodarski_oblik_naziv,
                    zemljista_naziv=zemljista_naziv
                )
                created = True

            if created:
                created_entries += 1
            else:
                existing_entries += 1

        print("Failed: {}".format(failed))
        print("Created: {}".format(created_entries))
        print("Existing: {}".format(existing_entries))
