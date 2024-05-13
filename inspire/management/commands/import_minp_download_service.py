import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from inspire.models import DownloadServiceEntryFeed
from django.urls import reverse
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = "Create a DownloadServiceEntryFeed instance with hardcoded values"

    def handle(self, *args, **options):
        # Use Site framework to get the current site's domain
        current_site = Site.objects.get_current()
        domain = current_site.domain

        title = "Ministarstvo Poljoprivrede - usluga preuzimanja - ATOM INSPIRE"
        subtitle = "Usluga preuzimanja za INSPIRE teme mrežna je usluga za preuzimanje unaprijed definiranih podataka pomoću ATOM tehnologije. Podaci su u formatu GML 3.2.1 u strukturi datoj INSPIRE specifikacijama i XML shemama u verziji 3.0. Mrežna usluga i podaci dostupni su za područje cijele Republike Hrvatske"
        link_to_download_service_iso19139 = "https://example.com/hardcoded-link"
        self_link = f"https://{domain}{reverse('download-service-feed')}"
        opensearch_link = f"https://{domain}{reverse('download-service-opensearch')}"
        rights = "Hardcoded Rights Information"
        author_name = "Hardcoded Author Name"
        author_email = "hardcoded@example.com"

        uid = uuid.uuid4()
        updated_on = timezone.now()

        DownloadServiceEntryFeed.objects.create(
            title=title,
            subtitle=subtitle,
            link_to_download_service_iso19139=link_to_download_service_iso19139,
            self_link=self_link,
            opensearch_link=opensearch_link,
            uid=uid,
            rights=rights,
            updated_on=updated_on,
            author_name=author_name,
            author_email=author_email,
        )

        self.stdout.write(
            self.style.SUCCESS("DownloadServiceEntryFeed instance created successfully!")
        )
