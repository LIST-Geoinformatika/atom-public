# Generated by Django 4.1 on 2024-03-27 08:53

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("inspire", "0002_rename_datasetservices_datasetservice"),
    ]

    operations = [
        migrations.CreateModel(
            name="DownloadServiceEntryFeed",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("title_EN", models.CharField(max_length=255)),
                ("subtitle", models.TextField()),
                ("subtitle_EN", models.TextField()),
                ("link_to_download_service_iso19139", models.URLField()),
                ("self_link", models.URLField()),
                ("opensearch_link", models.URLField()),
                ("uid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("rights", models.TextField()),
                ("rights_EN", models.TextField()),
                ("updated_on", models.DateTimeField(auto_now=True)),
                ("author_name", models.CharField(max_length=255)),
                ("author_name_EN", models.CharField(max_length=255)),
                ("author_email", models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name="ServiceFeed",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("title_EN", models.CharField(max_length=255)),
                ("uid", models.UUIDField(default=uuid.uuid4, editable=False)),
            ],
        ),
        migrations.RemoveField(
            model_name="datasetservicefeed",
            name="crs",
        ),
        migrations.RemoveField(
            model_name="datasetservicefeed",
            name="download_service_feed",
        ),
        migrations.RemoveField(
            model_name="datasetservicefeed",
            name="link_to_gml_file",
        ),
        migrations.RemoveField(
            model_name="datasetservicefeed",
            name="link_to_shapefile",
        ),
        migrations.RemoveField(
            model_name="datasetservicefeed",
            name="service",
        ),
        migrations.RemoveField(
            model_name="harmonizeddatasetfile",
            name="dataset_service_feed",
        ),
        migrations.AddField(
            model_name="datasetservicefeed",
            name="service_name",
            field=models.CharField(default=1, max_length=50, unique=True),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="DatasetService",
        ),
        migrations.DeleteModel(
            name="DownloadServiceFeed",
        ),
        migrations.AddField(
            model_name="servicefeed",
            name="dataset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="inspire.datasetservicefeed",
            ),
        ),
        migrations.AddField(
            model_name="datasetservicefeed",
            name="download_service_entry_feed",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="inspire.downloadserviceentryfeed",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="harmonizeddatasetfile",
            name="service_feed",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="inspire.servicefeed",
            ),
            preserve_default=False,
        ),
    ]