#!/usr/bin/env python3
import sys
from sqlalchemy import \
    Column, \
    ForeignKey, \
    Integer, \
    String, \
    create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Classes
class User(Base):
    __tablename__ = 'user'
    id = Column(
        Integer,
        primary_key = True
    )
    email = Column(
        String,
        nullable = False
    )

class Type(Base):
    __tablename__ = 'type'
    id = Column(
        Integer,
        primary_key = True
    )
    name = Column(
        String,
        nullable = False
    )
    description = Column(String)
    user_id = Column(
        Integer,
        ForeignKey('user.id'),
        nullable = False
    )

    user = relationship(User)

class Milk(Base):
    __tablename__ = 'milk'
    id = Column(
        Integer,
        primary_key = True
    )
    name = Column(
        String,
        nullable = False
    )
    user_id = Column(
        Integer,
        ForeignKey('user.id'),
        nullable = False
    )

    user = relationship(User)

class Cheese(Base):
    __tablename__ = 'cheese'
    id = Column(
        Integer,
        primary_key = True
    )
    name = Column(
        String,
        nullable = False
    )
    description = Column(String)
    place = Column(String)
    image = Column(String)
    type_id = Column(
        Integer,
        ForeignKey('type.id'),
        nullable = False
    )
    milk_id = Column(
        Integer,
        ForeignKey('milk.id'),
        nullable = False
    )
    user_id = Column(
        Integer,
        ForeignKey('user.id'),
        nullable = False
    )

    type = relationship(Type)
    milk = relationship(Milk)
    user = relationship(User)

    @property
    def object(self):
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type_id,
            'milk': self.milk_id,
            'place': self.place
        }
    @object.setter
    def update(self, object):
        self.name = object['name']
        self.description = object['description']
        self.place = object['place']
        self.type_id = object['type_id']
        self.milk_id = object['milk_id']

# initialisation
engine = create_engine('sqlite:///cheese.db')
Base.metadata.create_all(engine)
