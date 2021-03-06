# Generated by Django 2.2.9 on 2020-06-21 04:16

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djangorrules', '0002_auto_20200620_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='byweekday',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('1MO', 'First Monday'), ('1TU', 'First Tuesday'), ('1WE', 'First Wednesday'), ('1TH', 'First Thursday'), ('1FR', 'First Friday'), ('1SA', 'First Saturday'), ('1SU', 'First Sunday'), ('2MO', 'Second Monday'), ('2TU', 'Second Tuesday'), ('2WE', 'Second Wednesday'), ('2TH', 'Second Thursday'), ('2FR', 'Second Friday'), ('2SA', 'Second Saturday'), ('2SU', 'Second Sunday'), ('3MO', 'Third Monday'), ('3TU', 'Third Tuesday'), ('3WE', 'Third Wednesday'), ('3TH', 'Third Thursday'), ('3FR', 'Third Friday'), ('3SA', 'Third Saturday'), ('3SU', 'Third Sunday'), ('4MO', 'Fourth Monday'), ('4TU', 'Fourth Tuesday'), ('4WE', 'Fourth Wednesday'), ('4TH', 'Fourth Thursday'), ('4FR', 'Fourth Friday'), ('4SA', 'Fourth Saturday'), ('4SU', 'Fourth Sunday'), ('5MO', 'Fifth Monday'), ('5TU', 'Fifth Tuesday'), ('5WE', 'Fifth Wednesday'), ('5TH', 'Fifth Thursday'), ('5FR', 'Fifth Friday'), ('5SA', 'Fifth Saturday'), ('5SU', 'Fifth Sunday'), ('-1MO', 'Last Monday'), ('-1TU', 'Last Tuesday'), ('-1WE', 'Last Wednesday'), ('-1TH', 'Last Thursday'), ('-1FR', 'Last Friday'), ('-1SA', 'Last Saturday'), ('-1SU', 'Last Sunday')], default=None, max_length=174, null=True),
        ),
    ]
