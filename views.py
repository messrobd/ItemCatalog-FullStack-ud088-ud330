#!/usr/bin/env python3
from flask import \
    Flask, \
    render_template, \
    url_for
from models import \
    Base, \
    Type, \
    Milk, \
    Cheese
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
engine = create_engine('sqlite:///cheese.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

# session = DBSession()

# page view handlers
@app.route('/')
@app.route('/catalog')
def get_index():
    return render_template('catalog.html', \
        types=types, \
        cheeses=cheeses)

@app.route('/catalog/type/<int:type_id>')
def get_cheeses(type_id):
    cheeses_of_type = filter(lambda c: c.type == type_id, cheeses)
    return render_template('cheeses.html', \
        type=types[type_id], \
        cheeses=cheeses_of_type)

@app.route('/catalog/cheese/<int:cheese_id>')
def get_cheese(cheese_id):
    return render_template('cheese.html', cheese=cheeses[cheese_id])

@app.route('/catalog/cheese/new')
def new_cheese():
    return render_template('new_cheese.html', \
        types=types, \
        milks=milks)

@app.route('/catalog/cheese/<int:cheese_id>/edit')
def edit_cheese(cheese_id):
    return render_template('edit_cheese.html', \
        cheese=cheeses[cheese_id], \
        types=types, \
        milks=milks)

@app.route('/catalog/cheese/<int:cheese_id>/delete')
def delete_cheese(cheese_id):
    return render_template('delete_cheese.html', cheese=cheeses[cheese_id])

@app.route('/login')
def login():
    return 'login'


# start serving
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
