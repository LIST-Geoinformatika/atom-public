# Generated by Django 4.1 on 2024-03-26 08:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inspire", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="DatasetServices",
            new_name="DatasetService",
        ),
    ]
