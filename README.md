
## Developers

**Jose Serra -202208030** – backend developer
**Constanza Cifuentes -202208031** – backend developer
**María Rojas -202208025** – backend developer


---
## Description
This is the management service for a dairy company.
It uses an MVT

## Technologies

- Python 3.10
- Django 5.2.4
- MySQL


---

# Configuration



## Create virtual environment
python -m venv venv

## Activate virtual environment
### Windows:
venv\Scripts\activate
### Linux / Mac:
source venv/bin/activate

## *Install dependencies*

bash
pip install -r requirements.txt


## *Migrate the database*

bash
python manage.py migrate 

## Execute
python manage.py runserver

## Create Super User
python manage.py createsuperuser

