#!/usr/bin/env python


from datetime import datetime as dt
from datetime import timedelta, date
import calendar
import pandas as pd
import matplotlib.pyplot as plt
from django.contrib.auth.models import User
from django.db import IntegrityError

from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophee
)

########## À ADAPTER!!! ##########
user = User.objects.get(username='maykimay')
##################################

qs = ConsoCig.objects.filter(user=user).values()
qs2 = ConsoAlternative.objects.filter(user=user).values()

data_cig = pd.DataFrame(qs)
data_cig['type'] = 'smoke'
data_alter = pd.DataFrame(qs2)
data_alter['type'] = 'healthy'

data_cig['date'] = data_cig.apply(lambda r : dt.combine(r['date_cig'],r['time_cig']),1)
data_alter['date'] = data_alter.apply(lambda r : dt.combine(r['date_alter'],r['time_alter']),1)

frames = [data_cig, data_alter]
data = pd.concat(frames, ignore_index=True)

price_list = []
for pack_id in data.paquet_id:
    try:
        pack = Paquet.objects.get(id=pack_id)
        price_list.append(float(pack.price_per_cig))
    except ValueError:
        pass

data['price_per_cig'] = pd.Series(price_list)

##### moyenne par heure ######
hour = data[(data.type == 'smoke')].date.dt.hour.value_counts().sort_index()

#### cig par jour #####
daily_smoke = data[(data.type == 'smoke')].date.dt.date.value_counts().sort_index()
daily_money = data.set_index('date').price_per_cig.groupby(pd.Grouper(freq='D')).sum()

##### cig par semaine ######
weekly_smoke = data[(data.type == 'smoke')].date.dt.week.value_counts().sort_index()
weekly_money = data.set_index('date').price_per_cig.groupby(pd.Grouper(freq='W')).sum()

##### cig par mois ######
montly_smoke = data[(data.type == 'smoke')].date.dt.month.value_counts().sort_index()
montly_money = data.set_index('date').price_per_cig.groupby(pd.Grouper(freq='M')).sum()


##### consecutive dates without smoking #####

### get dataframe with all dates ###
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = UserProfile.objects.get(user=user).date_start
end_date = date.today()
dates = []
for single_date in daterange(start_date, end_date):
    dates.append({'date':pd.to_datetime(single_date)})

all_days_df = pd.DataFrame(dates, columns=['date']).set_index('date')

### get value_counts series with nb_cig per day ###
daily_smoke.rename("nb_cig", inplace=True)
daily_smoke.index = pd.to_datetime(daily_smoke.index)

# concats in dataframe and format as needed
all_days_df = pd.concat([all_days_df, daily_smoke], axis=1).rename(columns={"date_cig":"nb_cig"})
all_days_df.index.name = 'date'
all_days_df.reset_index(inplace=True)

nans_occur = all_days_df.nb_cig.isnull().astype(int).groupby(all_days_df.nb_cig.notnull().astype(int).cumsum()).sum()

trophees_no_smoking_days =[1, 2, 3, 4, 7]

Trophee.objects.filter(user=user).delete()

def trophee_no_smoking(nb):
    if nb in nans_occur:
        try:
            Trophee.objects.create(user=user, nb_cig=0, nb_jour=nb)
        except IntegrityError:
            pass

for nb_day in trophees_no_smoking_days:
    trophee_no_smoking(nb_day)

non_smoking_month = []
### for each month check if not smoked ###
for index, value in all_days_df.date.dt.month.value_counts().sort_index().items():
    # if complete month
    if value == calendar.monthrange(2020, index)[1]:
        filter_month = all_days_df[(all_days_df.date.dt.month == index)].isnull().values.any()
        if filter_month:
            ## one month without smoking
            non_smoking_month.append(True)
            try:
                Trophee.objects.create(user=user, nb_cig=0, nb_jour=30)
            except IntegrityError:
                pass
        else:
            non_smoking_month.append(False)
    else:
        non_smoking_month.append(False)

## 2 months without trophee
if any(non_smoking_month[i]==non_smoking_month[i+1] for i in range(len(non_smoking_month)-1)):
    Trophee.objects.create(user=user, nb_cig=0, nb_jour=60)


## exemple de double filtre
#data[(data.type == 'smoke') & (data.given == True)]
