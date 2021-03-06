# Generated by Django 3.0 on 2020-07-20 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0003_guest_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='limit_requests',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='party',
            name='starting_requests',
            field=models.IntegerField(default=5),
        ),
    ]
