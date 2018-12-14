from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///cheese.db')
DBSession = sessionmaker(bind=engine)

session = DBSession()

types = [
    Type(0, 'Blue cheese', 'moldy and good'),
    Type(1, 'Brown cheese', 'fudgy and weird')]
milks = [
    Milk('cow'),
    Milk('goat'),
    Milk('sheep'),
    Milk('buffalo')]
cheeses = [
    Cheese(0, 'stilton', 'Blue cheese', 'cow'),
    Cheese(1, 'gorgonzola', 'Blue cheese', 'cow'),
    Cheese(2, 'roquefort', 'Blue cheese', 'cow'),
    Cheese(3, 'selbu', 'Blue cheese', 'cow'),
    Cheese(4, 'shropshire', 'Blue cheese', 'cow')]
cheeses += [Cheese(5, 'Gudbrandsdalsost', 'Brown cheese', 'goat')]
