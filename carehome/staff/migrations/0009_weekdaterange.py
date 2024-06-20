# Generated by Django 5.0.6 on 2024-06-20 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0008_alter_timesheet_break_finished_time_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeekDateRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('week_number', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
    ]
