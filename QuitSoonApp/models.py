#!/usr/bin/env python
# pylint: disable=E5142 #User model imported from django.contrib.auth.models (imported-auth-user)

"""App models"""

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """User profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_start = models.DateField()
    starting_nb_cig = models.IntegerField()


class Paquet(models.Model):
    """Paquet model"""
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
    """ConsoCig model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime_cig = models.DateTimeField(null=True)
    # user_dt : calculation real dt user with tz_offset
    user_dt = models.DateTimeField(null=True, default=None)
    paquet = models.ForeignKey(Paquet, on_delete=models.CASCADE, null=True)
    given = models.BooleanField(default=False)

    def __str__(self):
        if self.paquet:
            paquet = self.paquet.type_cig
        else:
            paquet = None
        return "%s %s-%s" % (self.user, self.datetime_cig, paquet)

class Alternative(models.Model):
    """Alternative model"""

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
    """ConsoAlternative model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime_alter = models.DateTimeField(null=True)
    # user_dt : calculation real dt user with tz_offset
    user_dt = models.DateTimeField(null=True, default=None)
    alternative = models.ForeignKey(Alternative, on_delete=models.CASCADE)
    activity_duration = models.IntegerField(null=True)

class Objectif(models.Model):
    """Objectif model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qt = models.IntegerField(unique=True)
    datetime_creation = models.DateTimeField()
    datetime_objectif = models.DateTimeField()
    respected = models.BooleanField(default=False)


class Trophy(models.Model):
    """Trophy model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nb_cig = models.IntegerField()
    nb_jour = models.IntegerField()

    class Meta:
        unique_together = ('user', 'nb_cig', 'nb_jour',)
