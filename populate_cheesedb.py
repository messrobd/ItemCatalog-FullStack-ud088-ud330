from models import \
    Base, \
    User, \
    Type, \
    Milk, \
    Cheese
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///cheese.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

users = [
    User(email='messrobd@gmail.com'),
    User(email='robmessenger@yahoo.com')
]

types = [
    Type(name='Blue cheese', description='moldy and good', user_id=1),
    Type(name='Brown cheese', description='fudgy and weird', user_id=1)]

milks = [
    Milk(name='cow', user_id=1),
    Milk(name='goat', user_id=1)]

cheeses = [
    Cheese(name='stilton', type_id=1, milk_id=1, user_id=1),
    Cheese(name='Gudbrandsdalsost', type_id=2, milk_id=2, user_id=2)]

for u, t, m, c in zip(users, types, milks, cheeses):
    session.add(u)
    session.add(t)
    session.add(m)
    session.add(c)
    session.commit()

print(len(session.query(User).all()))
print(len(session.query(Type).all()))
print(len(session.query(Milk).all()))
print(len(session.query(Cheese).all()))

session.close()
