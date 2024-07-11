# Generated by Django 5.0.6 on 2024-07-03 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0005_week_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='week',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='week',
            name='staff_required',
        ),
        migrations.RemoveField(
            model_name='week',
            name='start_time',
        ),
        migrations.AddField(
            model_name='week',
            name='staff_required_1',
            field=models.IntegerField(default=0),
            preserve_default=0,
        ),
        migrations.AddField(
            model_name='week',
            name='staff_required_2',
            field=models.IntegerField(default=0),
            preserve_default=0,
        ),
        migrations.AddField(
            model_name='week',
            name='staff_required_3',
            field=models.IntegerField(default=0),
            preserve_default=0,
        ),
        migrations.AddField(
            model_name='week',
            name='staff_required_4',
            field=models.IntegerField(default=0),
            preserve_default=0,
        ),
    ]