#!/usr/bin/env python3
from flask import \
    Flask, \
    render_template, \
    url_for, \
    request, \
    redirect, \
    session as login_session
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
from oauth2client.client import flow_from_clientsecrets
import requests

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
    try:
        return session.query(kind).filter_by(**filter_args).one()
    except exc.NoResultFound:
        return None

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

@db_operation
def create_user(session, email):
    new_user = User(email=email)
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=email).one()
    return user.id

@db_operation
def get_user_id(session, email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except exc.NoResultFound:
        return None

# page view handlers
@app.route('/')
@app.route('/catalog')
def get_index():
    types = get_items(Type)
    user_name = login_session.get('user_name')
    return render_template('catalog.html', \
        user_name=user_name, \
        types=types)

@app.route('/catalog/type/<int:type_id>')
def get_cheeses(type_id):
    type = get_item(Type, id=type_id)
    cheeses_of_type = get_filtered_items(Cheese, type_id=type_id)
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
            place=request.form['place'], \
            user_id=login_session['user_id'])
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
    return render_template('login.html')

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # load the secret
    secret = 'static/client_secret.json'
    # get auth code from ajax request object
    auth_code = request.data
    # create a flow object from the client info in the secret
    oauth_flow = flow_from_clientsecrets(\
        secret, \
        scope='', \
        redirect_uri='postmessage')
    # exchange auth code for credentials
    credentials = oauth_flow.step2_exchange(auth_code)
    # get user info from google
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    user_info = requests.get(userinfo_url, params=params).json()
    # if the user is stored, log them in, else store them and log them in
    registered_user_id = get_user_id(user_info['email']) \
        or create_user(user_info['email'])
    # populate login session with user data
    login_session['user_id'] = registered_user_id
    login_session['user_name'] = user_info['name']
    login_session['access_token'] = credentials.access_token

    return user_info['name']

@app.route('/gdisconnect')
def gdisconnect():
    # build url to google revocation service
    revocation_url = 'https://accounts.google.com/o/oauth2/revoke?token=' \
        + login_session['access_token']
    # get response from revocation service
    revocation_result = requests.get(revocation_url).status_code
    del login_session['user_id']
    del login_session['user_name']
    del login_session['access_token']
    return redirect(url_for('get_index'))


@app.route('/testdb')
@db_operation
def get_users(session):
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
