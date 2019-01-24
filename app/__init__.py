#!/usr/bin/env python3
import os
from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from app.models import create_pg_engine


def get_config():
    try:
        return os.environ['APP_CONFIG']
    except KeyError:
        from configuration import DevConfig
        return DevConfig

app = Flask(__name__)
app.config.from_object(get_config())

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
