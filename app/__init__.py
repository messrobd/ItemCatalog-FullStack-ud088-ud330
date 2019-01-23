#!/usr/bin/env python3
from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from app.models import create_pg_engine


app = Flask(__name__)

# initialise db and create tables 
Base = declarative_base()
engine = create_pg_engine()
Base.metadata.create_all(engine)

# import views
from . import views
'''
@app.route('/')
def success():
    return 'Item catalog app is receiving you, over'
'''
