#!/usr/bin/env python3
from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from app.models import create_pg_engine

def create_app():
    app = Flask(__name__)

    # initialisation
    Base = declarative_base()
    engine = create_pg_engine()
    Base.metadata.create_all(engine)

    @app.route('/')
    def success():
        return 'Item catalog app is receiving you, over'

    return app
