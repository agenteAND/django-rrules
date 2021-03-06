# Generated by Django 2.2.9 on 2020-06-28 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangorrules', '0013_auto_20200628_0109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='year_month_mode',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(None, 'Select a mode'), (0, 'by date'), (1, 'by day')], default=None, null=True, verbose_name='mode'),
        ),
    ]
