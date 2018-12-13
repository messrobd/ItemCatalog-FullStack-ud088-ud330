#!/usr/bin/env python3

class Type():
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

class Milk():
    def __init__(self, name):
        self.name = name

class Cheese():
    def __init__(self, id, name, type, milk):
        self.id = id
        self.name = name
        self.type = type
        self.milk = milk
