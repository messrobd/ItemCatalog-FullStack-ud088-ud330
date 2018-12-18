#!/usr/bin/env python3
import os

# generate a random secret key for use in Flask app
# recommended code from http://flask.pocoo.org/docs/1.0/quickstart/#sessions
print(os.urandom(16))
