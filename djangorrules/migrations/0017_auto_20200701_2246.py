# Generated by Django 2.2.9 on 2020-07-01 22:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djangorrules', '0016_auto_20200701_0624'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recurrence',
            name='dt_start_is_included',
        ),
        migrations.CreateModel(
            name='RDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField()),
                ('naive_dt', models.DateField(blank=True)),
                ('naive_dt_time', models.TimeField(blank=True)),
                ('exclude', models.BooleanField(default=False)),
                ('recurrence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='r_dates', related_query_name='r_date', to='djangorrules.Recurrence')),
            ],
        ),
    ]
