#!/usr/bin/env python3
from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def success():
        return 'Item catalog app is receiving you, over'

    return app
