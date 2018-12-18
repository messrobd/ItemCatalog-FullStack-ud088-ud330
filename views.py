#!/usr/bin/env python3
from flask import \
    Flask, \
    render_template, \
    url_for, \
    request, \
    redirect, \
    session as app_session
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

@db_operation
def add_item(session, kind, **properties):
    new_item = kind(**properties)
    session.add(new_item)
    session.commit()

@db_operation
def edit_item(session, kind, id, **properties):
    item = get_item(kind, id=id)
    item.update(properties)
    session.add(item)
    session.commit()

@db_operation
def delete_item(session, kind, id):
    item = get_item(kind, id=id)
    session.delete(item)
    session.commit()

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

@app.route('/catalog/cheese/new', methods=['GET', 'POST'])
def new_cheese():
    if request.method == 'GET':
        types = get_items(Type)
        milks = get_items(Milk)
        return render_template('new_cheese.html', \
            types=types, \
            milks=milks)
    elif request.method == 'POST':
        add_item(Cheese, \
            name=request.form['name'], \
            type_id=int(request.form['type']), \
            description=request.form['description'], \
            milk_id=int(request.form['milk']), \
            place=request.form['place'])
        return redirect(url_for('get_index'))

@app.route('/catalog/cheese/<int:cheese_id>/edit', methods=['GET', 'POST'])
def edit_cheese(cheese_id):
    if request.method == 'GET':
        cheese = get_item(Cheese, id=cheese_id)
        types = get_items(Type)
        milks = get_items(Milk)
        return render_template('edit_cheese.html', \
            cheese=cheese, \
            types=types, \
            milks=milks)
    elif request.method == 'POST':
        edit_item(Cheese, cheese_id, \
            name=request.form['name'], \
            type_id=int(request.form['type']), \
            description=request.form['description'], \
            milk_id=int(request.form['milk']), \
            place=request.form['place'])
        return redirect(url_for('get_cheese', cheese_id=cheese_id))


@app.route('/catalog/cheese/<int:cheese_id>/delete', methods=['GET', 'POST'])
def delete_cheese(cheese_id):
    if request.method == 'GET':
        cheese = get_item(Cheese, id=cheese_id)
        return render_template('delete_cheese.html', cheese=cheese)
    elif request.method == 'POST':
        delete_item(Cheese, id=cheese_id)
        return redirect(url_for('get_index'))

@app.route('/login')
def login():
    return 'login'


# start serving
if __name__ == '__main__':
    app.secret_key = b'B\xe8\xa5\xba\xedk=\x1al@x\xd5\xa8\xbf\xe8f'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
