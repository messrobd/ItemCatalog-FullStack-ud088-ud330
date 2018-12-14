#!/usr/bin/env python3
from sqlalchemy import \
    Column, \
    ForeignKey, \
    Integer, \
    String, \
    create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

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
    type_id = Column(ForeignKey('type.id'))
    milk_id = Column(ForeignKey('milk.id'))

    type = relationship(Type)
    milk = relationship(Milk)

engine = create_engine('sqlite:///cheese.db')
Base.metadata.create_all(engine)
