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

# db operations
def db_operation(operation):
    def decorator(*args, **kwargs):
        session = DBSession()
        output = operation(session, *args, **kwargs)
        session.close()
        return output
    return decorator

@db_operation
def get_items(session, kind):
    return session.query(kind).all()

@db_operation
def get_filtered_items(session, kind, **filter_args):
    return session.query(kind).filter_by(**filter_args)

@db_operation
def get_item(session, kind, **filter_args):
    return session.query(kind).filter_by(**filter_args).one()

# page view handlers
@app.route('/')
@app.route('/catalog')
def get_index():
    types = get_items(Type)
    return render_template('catalog.html', types=types)

@app.route('/catalog/type/<int:type_id>')
def get_cheeses(type_id):
    type = get_item(Type, id=type_id)
    cheeses_of_type = get_filtered_items(Cheese, type_id=type_id)
    print('query executed')
    return render_template('cheeses.html', \
        type=type, \
        cheeses=cheeses_of_type)

@app.route('/catalog/cheese/<int:cheese_id>')
def get_cheese(cheese_id):
    cheese = get_item(Cheese, id=cheese_id)
    return render_template('cheese.html', cheese=cheese)

@app.route('/catalog/cheese/new')
def new_cheese():
    types = get_items(Type)
    milks = get_items(Milk)
    return render_template('new_cheese.html', \
        types=types, \
        milks=milks)

@app.route('/catalog/cheese/<int:cheese_id>/edit')
def edit_cheese(cheese_id):
    cheese = get_item(Cheese, id=cheese_id)
    types = get_items(Type)
    milks = get_items(Milk)
    return render_template('edit_cheese.html', \
        cheese=cheese, \
        types=types, \
        milks=milks)

@app.route('/catalog/cheese/<int:cheese_id>/delete')
def delete_cheese(cheese_id):
    cheese = get_item(Cheese, id=cheese_id)
    return render_template('delete_cheese.html', cheese=cheese)

@app.route('/login')
def login():
    return 'login'


# start serving
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
