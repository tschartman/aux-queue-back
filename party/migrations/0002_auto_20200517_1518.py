# Generated by Django 3.0 on 2020-05-17 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guest',
            name='blocked',
        ),
        migrations.AddField(
            model_name='guest',
            name='status',
            field=models.SmallIntegerField(default=0),
        ),
    ]
