#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


def application(environ, start_response):
    if not os.environ.get('APP_CONFIG'):
        os.environ['APP_CONFIG'] = environ['APP_CONFIG']
    from app import app as _application
    return _application(environ, start_response)
