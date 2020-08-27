#!/usr/bin/env python
import datetime
import pytz

from django.utils.timezone import make_aware
from django.db import models
import django.dispatch
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_start = models.DateField()
    starting_nb_cig = models.IntegerField()


class Paquet(models.Model):
    TYPE_CIG = [
        ('IND', 'Cigarettes'),
        ('ROL', 'Tabac à rouler'),
    ]
    UNIT = [
        ('U', 'Unités'),
        ('G', 'Grammes'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type_cig = models.CharField(
        max_length=8,
        choices=TYPE_CIG,
        default='IND',
    )
    brand = models.CharField(max_length=200)
    qt_paquet = models.IntegerField(default=20)
    unit = models.CharField(
        max_length=1,
        choices=UNIT,
        default='U',
    )
    price = models.DecimalField(max_digits=5, decimal_places=2)
    g_per_cig = models.DecimalField(max_digits=5, decimal_places=3, null=True)
    price_per_cig = models.DecimalField(max_digits=5, decimal_places=3, null=True)
    display = models.BooleanField(default=True)
    first = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'type_cig', 'brand', 'qt_paquet', 'price')

    def __str__(self):
        return "%s %s %s%s" % (self.type_cig, self.brand, self.qt_paquet, self.unit)


class ConsoCig(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_cig = models.DateField()
    time_cig = models.TimeField()
    datetime_cig = models.DateTimeField()
    user_dt = models.DateTimeField(null=True, default=None) # calculation real dt user
    paquet = models.ForeignKey(Paquet, on_delete=models.CASCADE, null=True)
    given = models.BooleanField(default=False)

    def __str__(self):
        if self.paquet:
            paquet = self.paquet.type_cig
        else:
            paquet = None
        return "%s %s-%s" % (self.user, self.date_cig, paquet)

@django.dispatch.receiver(models.signals.post_init, sender=ConsoCig)
def set_default_ConsoCig_datetime_cig(sender, instance, *args, **kwargs):
    """
    Set the default value for `datetime_cig` on the `instance`.
    :param sender: The `ConsoCig` class that sent the signal.
    :param instance: The `ConsoCig` instance that is being
        initialised.
    :return: None.
    """
    if not instance.datetime_cig:
        naive_datetime = datetime.datetime.combine(
            instance.date_cig,
            instance.time_cig,
            )
        instance.datetime_cig = make_aware(naive_datetime, pytz.utc)


class Alternative(models.Model):

    TYPE_ALTERNATIVE = [
        ('Ac', 'Activité'),
        ('Su', 'Substitut'),
    ]

    TYPE_ACTIVITY = [
        ('Sp', 'Sport'),
        ('Lo', 'Loisir'),
        ('So', 'Soin'),
    ]

    SUBSTITUT = [
        ('P', 'Patchs'),
        ('PAST', 'Pastilles'),
        ('GM', 'Gommes à mâcher'),
        ('GS', 'Gommes à sucer'),
        ('CS', 'Comprimés sublinguaux'),
        ('ECIG', 'Cigarette éléctronique'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type_alternative = models.CharField(
        max_length=2,
        choices=TYPE_ALTERNATIVE,
        default='Ac',
    )

    # ACTIVITY FIELDS #
    type_activity = models.CharField(
        max_length=2,
        choices=TYPE_ACTIVITY,
        null=True,
    )
    activity = models.CharField(max_length=200, null=True)

    # SUBSTITUT FIELDS #
    substitut = models.CharField(
        max_length=4,
        choices=SUBSTITUT,
        null=True,
    )
    nicotine = models.FloatField(null=True)
    display = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'type_alternative', 'activity', 'substitut', 'nicotine')


class ConsoAlternative(models.Model):
    ECIG_CHOICE = [
        ('V', "J'ai vapoté aujourd'hui"),
        ('S', "J'ai démarré un nouveau flacon"),
        ('VS', "J'ai vapoté aujourd'hui et démarré un nouveau flacon"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_alter = models.DateField()
    time_alter = models.TimeField()
    datetime_alter = models.DateTimeField()
    user_dt = models.DateTimeField(null=True, default=None) # calculation real dt user
    alternative = models.ForeignKey(Alternative, on_delete=models.CASCADE)
    activity_duration = models.IntegerField(null=True)
    ecig_choice = models.CharField(
        max_length=2,
        choices=ECIG_CHOICE,
        null=True,
    )

@django.dispatch.receiver(models.signals.post_init, sender=ConsoAlternative)
def set_default_ConsoAlternative_datetime_alter(sender, instance, *args, **kwargs):
    """
    Set the default value for `datetime_cig` on the `instance`.
    :param sender: The `ConsoCig` class that sent the signal.
    :param instance: The `ConsoCig` instance that is being
        initialised.
    :return: None.
    """
    if not instance.datetime_alter:
        naive_datetime = datetime.datetime.combine(
            instance.date_alter,
            instance.time_alter,
            )
        instance.datetime_alter = make_aware(naive_datetime, pytz.utc)


class Objectif(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qt = models.IntegerField(unique=True)
    datetime_creation = models.DateTimeField()
    datetime_objectif = models.DateTimeField()
    respected = models.BooleanField(default=False)


class Trophy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nb_cig = models.IntegerField()
    nb_jour = models.IntegerField()

    class Meta:
        unique_together = ('user', 'nb_cig', 'nb_jour',)
