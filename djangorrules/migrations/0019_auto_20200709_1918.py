# Generated by Django 2.2.9 on 2020-07-09 19:18

from django.db import migrations, models
from django.apps import apps

Recurrence = apps.get_model('djangorrules', 'recurrence')


class Migration(migrations.Migration):
    dependencies = [
        ('djangorrules', '0018_auto_20200709_1850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recurrence',
            name='timezone',
            field=models.CharField(choices=lambda: Recurrence.TIME_ZONE_LIST, max_length=30),
        ),
    ]
