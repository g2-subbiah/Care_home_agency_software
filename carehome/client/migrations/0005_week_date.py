# Generated by Django 5.0.6 on 2024-07-03 20:33

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0004_remove_week_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='week',
            name='date',
            field=models.DateField(default=datetime.date.today),
            preserve_default=False,
        ),
    ]