#!/usr/bin/env python3
from flask import \
    Flask, \
    render_template, \
    url_for, \
    request, \
    redirect, \
    session as login_session, \
    jsonify
from models import \
    Base, \
    User, \
    Type, \
    Milk, \
    Cheese
from sqlalchemy import create_engine
from sqlalchemy.orm import \
    sessionmaker, \
    exc
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests as auth_requests
import requests
import json

app = Flask(__name__)
engine = create_engine('sqlite:///cheese.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

CLIENT_ID = json.loads(
    open('static/client_secret.json', 'r').read())['web']['client_id']


# db operations
def db_operation(operation):
    '''Wrapper to scope requests to a session'''
    @wraps(operation)
    def session_wrapper(*args, **kwargs):
        session = DBSession()
        output = operation(session, *args, **kwargs)
        session.close()
        return output
    return session_wrapper


#   cheese CRUD functions
def get_items(session, kind):
    return session.query(kind).all()


def get_filtered_items(session, kind, **filter_args):
    return session.query(kind).filter_by(**filter_args).all()


def get_item(session, kind, **filter_args):
    try:
        return session.query(kind).filter_by(**filter_args).one()
    except exc.NoResultFound:
        return None


def add_item(session, kind, **properties):
    new_item = kind(**properties)
    session.add(new_item)
    session.commit()
    return new_item


def edit_item(session, kind, id, **properties):
    item = get_item(session, kind, id=id)
    item.deserialize = {**properties}
    session.add(item)
    session.commit()


def delete_item(session, kind, id):
    item = get_item(session, kind, id=id)
    session.delete(item)
    session.commit()


# users
def get_user_id(session, email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except exc.NoResultFound:
        return None


# request handlers
# page views
@app.route('/')
@app.route('/catalog')
@db_operation
def get_index(db_session):
    user_name = login_session.get('user_name')
    types = get_items(db_session, Type)
    types_catalog = [{
            'name': t.name,
            'cheeses': get_filtered_items(db_session, Cheese, type_id=t.id)
        } for t in types]
    return render_template('catalog.html',
                           client_id=CLIENT_ID,
                           user_name=user_name,
                           types=types_catalog)


@app.route('/catalog/type/<int:type_id>')
@db_operation
def get_cheeses(db_session, type_id):
    user_name = login_session.get('user_name')
    type = get_item(db_session, Type, id=type_id)
    cheeses_of_type = get_filtered_items(db_session, Cheese, type_id=type_id)
    return render_template('cheeses.html',
                           user_name=user_name,
                           type=type,
                           cheeses=cheeses_of_type)


@app.route('/catalog/cheese/<int:cheese_id>')
@db_operation
def get_cheese(db_session, cheese_id):
    loggedin_user = login_session.get('user_id')
    user_name = login_session.get('user_name')
    cheese = get_item(db_session, Cheese, id=cheese_id)
    type = get_item(db_session, Type, id=cheese.type_id)
    milk = get_item(db_session, Milk, id=cheese.milk_id)
    cheese_creator = cheese.user_id
    can_edit = cheese_creator == loggedin_user
    return render_template('cheese.html',
                           can_edit=can_edit,
                           cheese=cheese,
                           type=type,
                           milk=milk)


@app.route('/catalog/cheese/new', methods=['GET', 'POST'])
@db_operation
def new_cheese(db_session):
    if not login_session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'GET':
        types = get_items(db_session, Type)
        milks = get_items(db_session, Milk)
        preset_type = int(request.args.get('type')) if request.args else None
        return render_template('new_cheese.html',
                               types=types,
                               preset_type=preset_type,
                               milks=milks)
    elif request.method == 'POST':
        add_item(db_session, Cheese,
                 name=request.form['name'],
                 type_id=int(request.form['type']),
                 description=request.form['description'],
                 milk_id=int(request.form['milk']),
                 place=request.form['place'],
                 image=request.form['image'],
                 user_id=login_session['user_id'])
        return redirect(url_for('get_index'))


@app.route('/catalog/cheese/<int:cheese_id>/edit', methods=['GET', 'POST'])
@db_operation
def edit_cheese(db_session, cheese_id):
    cheese = get_item(db_session, Cheese, id=cheese_id)
    cheese_creator = cheese.user_id
    loggedin_user = login_session.get('user_id')
    if cheese_creator != loggedin_user:
        return redirect(url_for('login'))
    if request.method == 'GET':
        types = get_items(db_session, Type)
        milks = get_items(db_session, Milk)
        return render_template('edit_cheese.html',
                               cheese=cheese,
                               types=types,
                               milks=milks)
    elif request.method == 'POST':
        edit_item(db_session, Cheese, cheese_id,
                  name=request.form['name'],
                  type_id=int(request.form['type']),
                  description=request.form['description'],
                  milk_id=int(request.form['milk']),
                  place=request.form['place'],
                  image=request.form['image'])
        return redirect(url_for('get_cheese', cheese_id=cheese_id))


@app.route('/catalog/cheese/<int:cheese_id>/delete', methods=['GET', 'POST'])
@db_operation
def delete_cheese(db_session, cheese_id):
    cheese = get_item(db_session, Cheese, id=cheese_id)
    cheese_creator = cheese.user_id
    loggedin_user = login_session.get('user_id')
    if cheese_creator != loggedin_user:
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('delete_cheese.html', cheese=cheese)
    elif request.method == 'POST':
        referer = request.headers['Referer']
        delete_item(db_session, Cheese, id=cheese_id)
        return redirect(referer)


@app.route('/login')
def login():
    referer = request.headers['Referer']
    return render_template('login.html',
                           client_id=CLIENT_ID,
                           referer=referer)


# json endpoints
@app.route('/api/v1/cheeses')
@db_operation
def get_cheeses_json(db_session):
    return \
        jsonify(cheeses=[c.serialize for c in get_items(db_session, Cheese)])


@app.route('/api/v1/cheese/<int:cheese_id>')
@db_operation
def get_cheese_json(db_session, cheese_id):
    return jsonify(get_item(db_session, Cheese, id=cheese_id).object)


# authorisation flow
@app.route('/tokensignin', methods=['POST'])
@db_operation
def tokensignin(db_session):
    token_in = request.data
    client_id = json.loads(
        open('static/client_secret.json', 'r').read())['web']['client_id']
    try:
        id_info = id_token.verify_oauth2_token(
            token_in,
            auth_requests.Request(),
            client_id)
        if id_info['iss'] not in [
                'accounts.google.com',
                'https://accounts.google.com']:
            raise ValueError('wrong issuer')
    except ValueError:
        pass
    else:
        registered_user_id = get_user_id(db_session, id_info['email']) \
                or add_item(db_session, User, email=id_info['email']).id
        login_session['user_id'] = registered_user_id
        login_session['user_name'] = id_info['name']
        return id_info['name']


@app.route('/signout')
def sign_out():
    referer = request.headers['Referer']
    del login_session['user_id']
    del login_session['user_name']
    return redirect(referer)


# testing
@app.route('/testdb')
@db_operation
def get_users(db_session):
    output = ''
    i = 0
    for u in session.query(Cheese).all():
        output += str(u.id)
        output += str(u.__dict__)
        output += '</br>'
        i += 1
    output += str(i)
    return output


# start serving
if __name__ == '__main__':
    app.secret_key = b'B\xe8\xa5\xba\xedk=\x1al@x\xd5\xa8\xbf\xe8f'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
