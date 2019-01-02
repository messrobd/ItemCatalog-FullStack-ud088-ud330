#!/usr/bin/env python3
from models import \
    Base, \
    User, \
    Type, \
    Milk, \
    Cheese
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///cheese.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

new = Cheese(name='Gruyere', type_id=3, milk_id=1, user_id=1)
session.add(new)
new.deserialize = {'name': None,
                'type_id': 3,
                'description': None,
                'milk_id': 1,
                'place': None,
                'image': None}

try:
    session.commit()
except exc.IntegrityError as i:
    session.rollback()
    print(i.args[0])

session.close()
