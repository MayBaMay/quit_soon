# Generated by Django 3.0.5 on 2020-08-06 14:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuitSoonApp', '0002_auto_20200728_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='consoalternative',
            name='datetime_alter',
            field=models.DateTimeField(),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='consocig',
            name='datetime_cig',
            field=models.DateTimeField(),
            preserve_default=False,
        ),
    ]
