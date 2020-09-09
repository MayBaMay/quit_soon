# quit_soon
Projet #13 Openclassrooms Python


This open source project was created for the OpenClassRooms' Python developer course (Project 13/13)). It is a DJANGO application integrating a back-end part based on Python 3.7.

This app helps user to track its smoking habits and helps to reduce it in order to quit permanently.<br/>
The user, once connected to its account, fill:
* A user profile with smoking habits when starting using the app,
* Type (roll-your-own and manufactured cigarettes), brand, price of cigarette pack (and amount of tabacco in rolled cigarette) in order to calculate the most precisely possible how much the user spent each time he smokes,
* each cigarette smoked
* At the mean time, the user can track all the alternatives used in order to avoid smoking. It can be nicotine substitutes, sport, leisure activities or health care. It allows user to value all those ways to fight against temptation.
* each alternative used (with nicotine for nicotine substitutes and duration for activities)

The app displays stats showing user informations with the data entered and allows him/her to obtain trophees in each step of the reduction process.

## How to install this project

### 1 - Fork the project
### 2 - Clone the project on your PC
### 3 - Create and set the database
This project was conceived with postgresql, but we can use an other db engine.

#### STEP 1 : Create a database.
(with postgresql)<br/>
`createdb <your database name>`

#### STEP 2: Create your virtualenv
(on mac and linux)<br/>
`cd quit_soon`<br/>
`virtualenv env -p python3`<br/>
`source env/bin/activate`<br/>
`pip install -r requirements.txt`<br/>

#### STEP 3 : Create a setting file pur_beurre_project/settings/.env
```
SECRET_KEY = '<your secret key>'

DB_NAME = '<your database name>'
DB_USER = '<your database username>'
DB_PASSWORD = '<your database password>'
DB_HOST = ''
DB_PORT = '5432'

```

#### STEP 4 : Migrate the model into the database
`./manage.py migrate`


### 4 - Launch project
`./manage.py runserver`
With your usual browser, use the application on url http://127.0.0.1:8000/

## Find the project online

This project can be tested on url http://nicotinekill.com/<br/>

## Next Steps
* improve app presentation
* improve, and possibly, add new graphs, stats...
*
