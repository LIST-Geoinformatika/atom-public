import os
import subprocess
import zipfile
from django.core.management.base import BaseCommand
from inspire.models import DownloadServiceEntryFeed, DatasetServiceFeed, CRS
from django.utils import timezone
from django.urls import reverse
import uuid
from django.conf import settings
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = "Prepare GospodarskeJedinice instances for DatasetServiceFeed"

    def create_shapefile(self, output_fpath, sql_query):
        # Use ogr2ogr to export directly to Shapefile
        ogr2ogr_command = [
            "ogr2ogr",
            "-f",
            "ESRI Shapefile",
            output_fpath,
            "PG:host={} port={} dbname={} user={} password={}".format(
                settings.DATABASES["default"]["HOST"],
                settings.DATABASES["default"]["PORT"],
                settings.DATABASES["default"]["NAME"],
                settings.DATABASES["default"]["USER"],
                settings.DATABASES["default"]["PASSWORD"],
            ),
            "-sql",
            sql_query,
            "-lco",
            "ENCODING=UTF-8",
        ]

        subprocess.run(ogr2ogr_command, check=True)

        # Create the .cpg file for the main shapefile
        cpg_file_path = os.path.splitext(output_fpath)[0] + ".cpg"
        with open(cpg_file_path, "w") as cpg_file:
            cpg_file.write("UTF-8")

        return cpg_file_path

    def handle(self, *args, **options):
        # Use Site framework to get the current site's domain
        current_site = Site.objects.get_current()
        domain = current_site.domain

        # Assuming you have a DownloadServiceEntryFeed instance to associate with
        download_service_feed = DownloadServiceEntryFeed.objects.first()

        # Specify your SQL query here
        sql_query = "SELECT * FROM inspire_gospodarskajedinica"

        # Create temp dir
        request_uid = str(uuid.uuid4())
        data_dir = os.path.join(settings.DATA_DIR, request_uid)
        os.makedirs(data_dir, exist_ok=True)
        output_fpath = os.path.join(data_dir, "output.shp")

        # Call the utility function to create the shapefile
        cpg_file_path = self.create_shapefile(output_fpath, sql_query)

        # Create a ZIP file and add the Shapefile to it
        zip_filename = os.path.join(data_dir, "gospodarske-jedinice.zip")
        relative_zip_path = os.path.relpath(zip_filename, settings.DATA_DIR)
        with zipfile.ZipFile(zip_filename, "w") as zip_file:
            # Add the generated Shapefile files to the ZIP file
            for extension in [".shp", ".shx", ".dbf", ".prj"]:
                filename = os.path.splitext(output_fpath)[0] + extension
                zip_file.write(filename, arcname=os.path.basename(filename))

            # Add the .cpg file to the ZIP file
            zip_file.write(cpg_file_path, arcname=os.path.basename(cpg_file_path))

        # Now, create the DatasetServiceFeed instance
        dataset_service_feed = DatasetServiceFeed.objects.create(
            download_service_feed=download_service_feed,
            service_name="gospodarska-jedinica-suma",
            title="Gospodarska jedinica šuma šumoposjednika",
            subtitle="Subtitle",
            self_link=reverse("dataset-feed", args=["gospodarska-jedinica-suma"]),
            rights="Rights information",
            updated_on=timezone.now(),
            author_name="Author Name",
            author_email="author@example.com",
            link_to_shapefile=f"https://{domain}{os.path.join(settings.DATA_URL, relative_zip_path)}",
            uid=uuid.uuid4(),
            summary="Summary",
            metadata_record="https://test-geokatalog.mps.hr/geonetwork/srv/eng/catalog.search#/metadata/44aebee3-9d00-4828-a550-6d7a8454d85b",
        )

        # Fetch all existing CRS instances
        existing_crs_instances = CRS.objects.all()

        # Add the existing CRS instances to the dataset_service_feed
        dataset_service_feed.crs.add(*existing_crs_instances)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created DatasetServiceFeed: {dataset_service_feed.title}"
            )
        )
