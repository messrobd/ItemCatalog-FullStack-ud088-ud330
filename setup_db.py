#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.models import (
    Base,
    User,
    Type,
    Milk,
    Cheese,
    create_pg_engine)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.views import db_operation


@db_operation
def add_items(db_session, items):
    for i in items:
        db_session.add(i)
    db_session.commit()
    print('{} items added'.format(len(items)))


# initialise db and create tables
engine = create_pg_engine()
Base.metadata.create_all(engine)
Base.metadata.bind = engine

# populate db with sample data
users = [
    User(email='messrobd@gmail.com'),
    User(email='gunnsa.robertsdottir@gmail.com')
]

types = [
    Type(name='Blue cheese', description='moldy and good', user_id=1),
    Type(name='Brown cheese', description='fudgy and weird', user_id=1),
    Type(name='Hard cheese', description='Yellow and gnarly', user_id=1),
    Type(name='Washed-rind cheese', description='White and runny', user_id=1),
]

milks = [
    Milk(name='cow', user_id=1),
    Milk(name='goat', user_id=1),
    Milk(name='ewe', user_id=1)
]

cheeses = [
    Cheese(name='Stilton', type_id=1, milk_id=1, user_id=1),
    Cheese(name='Gudbrandsdalsost', type_id=2, milk_id=2, user_id=2),
    Cheese(name='Cheddar', type_id=3, milk_id=1, user_id=1),
    Cheese(name='Brie', type_id=4, milk_id=1, user_id=1)
]

add_items(users)
add_items(types)
add_items(milks)
add_items(cheeses)
