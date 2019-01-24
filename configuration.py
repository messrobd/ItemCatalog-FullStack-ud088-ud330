#!/usr/bin/env python3
import os

root_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    SECRET_KEY = b'B\xe8\xa5\xba\xedk=\x1al@x\xd5\xa8\xbf\xe8f'
    CLIENT_SECRET = root_dir + '/app/static/client_secret.json'

class DevConfig(Config):
    DEBUG = True
