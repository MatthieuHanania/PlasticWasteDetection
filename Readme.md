# Project Plastic detection

The objective of this project is to identify plastic bottle in pictures.

This project is based on a real use case : the detection of waste in river.

## Composition


## Installation

To install the dependeces (it is recommanded to use a virtual environnement)
> pip install -r requirements.txt


## Execution

This tool use Django. When executed, it will run a website

> python manage.py runserver

By defalt, the access ip is http://127.0.0.1:8000/dataction/

## Intercace

After accessing to the home page, 4 pages are availables:

**Soumettre une image**: this page allows you to upload an image , the AI will analyse it and highlight the potential plastic bottle.
-> bouteille.PNG

if a bottle is detected, the metadata of the picture will be added in a database.

**Carte des déchets** : This interactive map displays all the waste geolocalisation from the database.

**Liste des points GPS**: This represent the database, we can select each point and vizualise it on the map

## The automatic detection

To detect plastic bottles in the pictures, we download an already trained model made by tensorflow.
