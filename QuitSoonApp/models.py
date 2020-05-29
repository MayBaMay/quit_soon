#!/usr/bin/env python

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_start = models.DateField()
    starting_nb_cig = models.IntegerField()


class Paquet(models.Model):
    TYPE_CIG = [
        ('IND', 'Cigarettes industrielles'),
        ('ROL', 'Cigarettes roulées'),
        ('CIGARES', 'Cigares'),
        ('PIPE', 'Pipe'),
        ('NB', 'Autres(en nb/paquet)'),
        ('GR', 'Autres(en g/paquet)'),
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
    g_per_cig = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    price_per_cig = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    display = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'type_cig', 'brand', 'qt_paquet', 'price')

    def __str__(self):
        return "%s %s %s%s" % (self.type_cig, self.brand, self.qt_paquet, self.unit)


class ConsoCig(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_cig = models.DateField()
    time_cig = models.TimeField()
    paquet = models.ForeignKey(Paquet, on_delete=models.CASCADE, null=True)
    given = models.BooleanField(default=False)

    def __str__(self):
        return "%s %s-%s" % (self.user, self.date_cig, self.paquet.type_cig)


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
        ('P24', 'Patchs(24h)'),
        ('P16', 'Patchs(16h)'),
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
    alternative = models.ForeignKey(Alternative, on_delete=models.CASCADE)
    activity_duration = models.IntegerField(null=True)
    ecig_choice = models.CharField(
        max_length=2,
        choices=ECIG_CHOICE,
        null=True,
    )


class Objectif(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qt = models.IntegerField(unique=True)
    datetime_creation = models.DateTimeField()
    datetime_objectif = models.DateTimeField()
    respected = models.BooleanField(default=False)


class Trophee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nb_cig = models.IntegerField()
    nb_jour = models.IntegerField()

    class Meta:
        unique_together = ('nb_cig', 'nb_jour',)
