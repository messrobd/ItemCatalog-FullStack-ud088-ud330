from models import \
    Base, \
    Type, \
    Milk, \
    Cheese
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///cheese.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

types = [
    Type(name='Blue cheese', description='moldy and good'),
    Type(name='Brown cheese', description='fudgy and weird')]

milks = [
    Milk(name='cow'),
    Milk(name='goat')]

cheeses = [
    Cheese(name='stilton', type_id=1, milk_id=1),
    Cheese(name='Gudbrandsdalsost', type_id=2, milk_id=2)]

for t, m, c in zip(types, milks, cheeses):
    session.add(t)
    session.add(m)
    session.add(c)
    session.commit()

session.close()
