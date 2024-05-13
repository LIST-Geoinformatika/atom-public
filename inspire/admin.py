from django.contrib import admin

from inspire import models


@admin.register(models.DownloadServiceEntryFeed)
class DownloadServiceEntryFeedAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle")


@admin.register(models.DatasetServiceFeed)
class DatasetServiceFeedAdmin(admin.ModelAdmin):
    list_display = ("title",)


@admin.register(models.ServiceFeed)
class ServiceFeedAdmin(admin.ModelAdmin):
    list_display = ("title",)


@admin.register(models.CRS)
class CRSAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "epsg_code")


@admin.register(models.HarmonizedDatasetFile)
class HarmonizedDatasetFileAdmin(admin.ModelAdmin):
    list_display = ("id", "service_feed", "crs")
