import os
import uuid

from django.contrib.gis.db import models as geomodels
from django.db import models

from inspire.utils.storage import RssStorage

RSS_FS = RssStorage()


class CRS(models.Model):
    epsg_code = models.IntegerField()
    label = models.CharField(max_length=255)

    @property
    def opengis_label(self):
        base_link = "http://www.opengis.net/def/crs/EPSG/0/"
        return f"{base_link}{self.epsg_code}"

    def __str__(self):
        return self.label

    class Meta:
        verbose_name_plural = "CRS"


class DownloadServiceEntryFeed(models.Model):
    title = models.CharField(max_length=255)
    title_EN = models.CharField(max_length=255)
    subtitle = models.TextField()
    subtitle_EN = models.TextField()
    link_to_download_service_iso19139 = models.URLField()
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    rights = models.TextField()
    rights_EN = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)
    author_name = models.CharField(max_length=255)
    author_name_EN = models.CharField(max_length=255)
    author_email = models.EmailField()

    def __str__(self):
        return self.title


class DatasetServiceFeed(models.Model):
    download_service_entry_feed = models.ForeignKey(
        DownloadServiceEntryFeed,
        on_delete=models.CASCADE,
    )
    service_name = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    title_EN = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    subtitle_EN = models.CharField(max_length=255)
    rights = models.TextField()
    rights_EN = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)
    author_name = models.CharField(max_length=255)
    author_email = models.EmailField()
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    summary = models.TextField()
    summary_EN = models.TextField()
    metadata_record = models.URLField()
    spatial_dataset_identifier_namespace = models.URLField()
    spatial_dataset_identifier_code = models.CharField(max_length=255)
    available_crs = models.ManyToManyField(CRS)

    def __str__(self):
        return f"Dataset Service Feed - {self.title}"


class ServiceFeed(models.Model):
    dataset = models.ForeignKey(DatasetServiceFeed, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    title_EN = models.CharField(max_length=255)
    uid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"Dataset Service Feed - {self.title}"


class HarmonizedDatasetFile(models.Model):
    service_feed = models.ForeignKey(ServiceFeed, on_delete=models.CASCADE)
    uploaded_on = models.DateTimeField(auto_now=True)
    crs = models.ForeignKey(CRS, on_delete=models.CASCADE)
    file = models.FileField(upload_to="harmonized/", null=True, blank=False)

    def __str__(self):
        return f"Harmonized Dataset File - {self.service_feed} ({self.crs.epsg_code})"

    class Meta:
        verbose_name_plural = "Harmonized Dataset Files"
