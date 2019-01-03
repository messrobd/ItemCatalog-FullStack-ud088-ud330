#!/usr/bin/env python3
import sys
from sqlalchemy import \
    Column, \
    ForeignKey, \
    Integer, \
    String, \
    create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import \
    relationship, \
    validates

Base = declarative_base()


# Classes
class User(Base):
    __tablename__ = 'user'
    id = Column(
        Integer,
        primary_key=True
    )
    email = Column(
        String,
        nullable=False
    )


class Type(Base):
    __tablename__ = 'type'
    id = Column(
        Integer,
        primary_key=True
    )
    name = Column(
        String,
        nullable=False
    )
    description = Column(String)
    user_id = Column(
        Integer,
        ForeignKey('user.id'),
        nullable=False
    )

    user = relationship(User)


class Milk(Base):
    __tablename__ = 'milk'
    id = Column(
        Integer,
        primary_key=True
    )
    name = Column(
        String,
        nullable=False
    )
    user_id = Column(
        Integer,
        ForeignKey('user.id'),
        nullable=False
    )

    user = relationship(User)


class Cheese(Base):
    __tablename__ = 'cheese'
    id = Column(
        Integer,
        primary_key=True
    )
    name = Column(
        String,
        nullable=False
    )
    description = Column(String)
    place = Column(String)
    image = Column(String)
    type_id = Column(
        Integer,
        ForeignKey('type.id'),
        nullable=False
    )
    milk_id = Column(
        Integer,
        ForeignKey('milk.id'),
        nullable=False
    )
    user_id = Column(
        Integer,
        ForeignKey('user.id'),
        nullable=False
    )

    type = relationship(Type)
    milk = relationship(Milk)
    user = relationship(User)

    @validates('name', 'type_id', 'milk_id', 'user_id')
    def typecheck_fields(self, key, field):
        '''Performs type-checking of required properties '''
        try:
            if key == 'name':
                assert type(field) == str and field is not '', \
                    'Name must be a non-empty string'
            else:
                assert type(field) == int, \
                    '{key} must be an integer'.format(key=key)
        except AssertionError as a:
            raise ValueError(a.args[0])
        else:
            return field

    @property
    def serialize(self):
        '''Returns the writable properties of the object as a dictionary '''
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type_id,
            'milk': self.milk_id,
            'place': self.place,
            'image': self.image
        }

    @serialize.setter
    def deserialize(self, properties):
        '''Given a dictionary, updates the writable properties of the
        object '''
        self.name = properties['name']
        self.description = properties['description']
        self.place = properties['place']
        self.type_id = properties['type_id']
        self.milk_id = properties['milk_id']
        self.image = properties['image']


# initialisation
engine = create_engine('sqlite:///cheese.db')
Base.metadata.create_all(engine)
