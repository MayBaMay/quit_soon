# Generated by Django 3.0.5 on 2020-05-21 14:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('QuitSoonApp', '0014_auto_20200521_1505'),
    ]

    operations = [
        migrations.AddField(
            model_name='alternative',
            name='activity',
            field=models.CharField(choices=[('Ac', 'Activité'), ('Su', 'Substitut')], default='Sp', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='alternative',
            name='type_alternative',
            field=models.CharField(choices=[('Ac', 'Activité'), ('Su', 'Substitut')], default='AC', max_length=200),
        ),
        migrations.AlterUniqueTogether(
            name='alternative',
            unique_together={('user', 'type_alternative', 'activity', 'substitut', 'nicotine')},
        ),
        migrations.RemoveField(
            model_name='alternative',
            name='alternative',
        ),
    ]
