# Generated by Django 4.0.8 on 2022-10-18 07:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_dns", "0016_cleanup_ptr_records"),
    ]

    operations = [
        migrations.AlterField(
            model_name="record",
            name="ttl",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
