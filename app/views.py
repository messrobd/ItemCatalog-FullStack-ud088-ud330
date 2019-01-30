#!/usr/bin/env python3
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    redirect,
    session as login_session,
    jsonify)
from app import app
from app.models import (
    Base,
    User,
    Type,
    Milk,
    Cheese,
    create_pg_engine)
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    exc)
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests as auth_requests
import requests
import json
from werkzeug.exceptions import (
    NotFound,
    Forbidden,
    BadRequest)


engine = create_pg_engine()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

CLIENT_ID = json.loads(
    open(app.config['CLIENT_SECRET'], 'r').read())['web']['client_id']


# db operations
def db_operation(operation):
    '''Wrapper to scope web server requests to a db session. Ensures the
    session is closed in the event that a request throws an exception '''
    @wraps(operation)
    def session_wrapper(*args, **kwargs):
        session = DBSession()
        try:
            output = operation(session, *args, **kwargs)
        except Exception:
            raise
        else:
            return output
        finally:
            session.close()
    return session_wrapper


# cheese CRUD functions
def get_items(session, kind):
    '''Get all items of the given kind from the db. 'kind' must be a sqlalchemy
    modelled object'''
    return session.query(kind).all()


def get_filtered_items(session, kind, **filter_args):
    '''Get all items of the given kind, filtered by the given args, from the
    db. 'kind' must be a sqlalchemy modelled object, 'filter_args' are assumed
    to be properties of the given kind '''
    return session.query(kind).filter_by(**filter_args).all()


def get_item(session, kind, **filter_args):
    '''Gets exactly one of the given kind, selected by the given args, from
    the db, or raises an exception. 'kind' must be a sqlalchemy modelled
    object '''
    try:
        return session.query(kind).filter_by(**filter_args).one()
    except exc.NoResultFound:
        raise KeyError


def add_item(session, kind, **properties):
    '''Adds an object of the given kind, with the given properties, to the db.
    Returns the new object, or raises an exception in the event that it fails
    validation. 'kind' must be a sqlalchemy modelled object '''
    try:
        new_item = kind(**properties)
    except ValueError:
        raise
    else:
        session.add(new_item)
    try:
        session.commit()
    except exc.IntegrityError as i:
        session.rollback()
        raise ValueError(i.args[0])
    else:
        return new_item


def edit_item(session, kind, id, **properties):
    '''Edits an object of the given kind, overwriting its properties with those
    provided. Returns the new object, or raises an exception in the event that
    it fails validation. 'kind' must be a sqlalchemy modelled object '''
    try:
        item = get_item(session, kind, id=id)
    except KeyError:
        raise
    try:
        item.deserialize = properties
    except ValueError:
        raise
    else:
        session.add(item)
    try:
        session.commit()
    except exc.IntegrityError as i:
        session.rollback()
        raise ValueError(i.args[0])
    else:
        return item


def delete_item(session, kind, id):
    '''Deletes the given object from the db. 'kind' must be a sqlalchemy
    modelled object '''
    try:
        item = get_item(session, kind, id=id)
    except KeyError:
        raise
    else:
        session.delete(item)
    session.commit()


# users
def get_user_id(session, email):
    ''' Given an email, returns the ID of the corresponding user, or none if
    the user is not registered '''
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
    '''Serves the view for the homepage. Gets all cheeses in the db, grouped
    by type, and returns the 'catalog' template. If the user is logged in, the
    option to create a cheese will be afforded '''
    user_name = login_session.get('user_name')
    types = get_items(db_session, Type)
    types_catalog = [{
            'name': t.name,
            'cheeses': get_filtered_items(db_session, Cheese, type_id=t.id)
        } for t in types]
    return render_template('catalog.html',
                           user_name=user_name,
                           client_id=CLIENT_ID,
                           types=types_catalog)


@app.route('/catalog/type/<int:type_id>')
@db_operation
def get_cheeses(db_session, type_id):
    '''Serves the view for a type of cheese '''
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
    '''Serves the view for a cheese. If the logged-user created the cheese, the
    options to edit and delete it will be afforded. In the event that a
    non-existant cheese is requested, a 404 error will be returned '''
    loggedin_user = login_session.get('user_id')
    try:
        cheese = get_item(db_session, Cheese, id=cheese_id)
    except KeyError:
        raise NotFound(
              'No cheese with id {} could be found.'.format(cheese_id))
    else:
        cheese_creator = cheese.user_id
        can_edit = cheese_creator == loggedin_user
        user_name = login_session.get('user_name')
        return render_template('cheese.html',
                               user_name=user_name,
                               can_edit=can_edit,
                               cheese=cheese)


@app.route('/catalog/cheese/new', methods=['GET', 'POST'])
@db_operation
def new_cheese(db_session):
    ''' Serves the form for creating a new cheese, and responds to the POST
    request on form submission. Required fields are enforced by the client;
    server validation is also performed on submission '''
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
        try:
            new_cheese = add_item(db_session, Cheese,
                                  name=request.form['name'],
                                  type_id=int(request.form['type']),
                                  description=request.form['description'],
                                  milk_id=int(request.form['milk']),
                                  place=request.form['place'],
                                  image=request.form['image'],
                                  user_id=login_session['user_id'])
        except ValueError as v:
            raise BadRequestr(v.args[0])
        else:
            return redirect(url_for('get_cheese', cheese_id=new_cheese.id))


@app.route('/catalog/cheese/<int:cheese_id>/edit', methods=['GET', 'POST'])
@db_operation
def edit_cheese(db_session, cheese_id):
    '''Serves the form for editing a cheese, and responds to the POST
    request on form submission. Authorisation check is performed on all
    requests, resulting in a Forbidden error in the event of failure. Required
    fields are enforced by the client; server validation is also performed on
    submission '''
    loggedin_user = login_session.get('user_id')
    user_name = login_session.get('user_name')
    if not loggedin_user:
        return redirect(url_for('login'))
    try:
        cheese = get_item(db_session, Cheese, id=cheese_id)
    except KeyError:
        raise NotFound(
              'No cheese with id {} could be found.'.format(cheese_id))
    else:
        cheese_creator = cheese.user_id
        if cheese_creator != loggedin_user:
            raise Forbidden(
                  'You are not authorised to edit {}.'.format(cheese.name))
        if request.method == 'GET':
            types = get_items(db_session, Type)
            milks = get_items(db_session, Milk)
            return render_template('edit_cheese.html',
                                   cheese=cheese,
                                   types=types,
                                   milks=milks)
        elif request.method == 'POST':
            try:
                edit_item(db_session, Cheese, cheese_id,
                          name=request.form['name'],
                          type_id=int(request.form['type']),
                          description=request.form['description'],
                          milk_id=int(request.form['milk']),
                          place=request.form['place'],
                          image=request.form['image'])
            except KeyError:
                raise NotFound(
                      'No cheese with id {} could be found.'.format(cheese_id))
            except ValueError as v:
                raise BadRequest(v.args[0])
            else:
                return redirect(url_for('get_cheese', cheese_id=cheese_id))


@app.route('/catalog/cheese/<int:cheese_id>/delete', methods=['GET', 'POST'])
@db_operation
def delete_cheese(db_session, cheese_id):
    '''Serves a confirmation request on deletion of a cheese, and responds to
    the POST request on confirmation. Authorisation check is performed on all
    requests, resulting in a Forbidden error in the event of failure. '''
    loggedin_user = login_session.get('user_id')
    if not loggedin_user:
        return redirect(url_for('login'))
    try:
        cheese = get_item(db_session, Cheese, id=cheese_id)
    except KeyError:
        raise NotFound(
              'No cheese with id {} could be found.'.format(cheese_id))
    else:
        cheese_creator = cheese.user_id
        if cheese_creator != loggedin_user:
            raise Forbidden(
                  'You are not authorised to delete {}.'.format(cheese.name))
        if request.method == 'GET':
            return render_template('delete_cheese.html', cheese=cheese)
        elif request.method == 'POST':
            referrer = request.headers.get('Referer') or '/'
            try:
                delete_item(db_session, Cheese, id=cheese_id)
            except KeyError:
                raise NotFound(
                      'No cheese with id {} could be found.'.format(cheese_id))
            else:
                return redirect(referrer)


@app.route('/login')
def login():
    '''Serves the login page. User id is obtained via Google authentication and
    passed to the server by JS embedded in the login template '''
    referrer = request.headers.get('Referer') or '/'
    return render_template('login.html',
                           client_id=CLIENT_ID,
                           referrer=referrer)


# authorisation flow
@app.route('/tokensignin', methods=['POST'])
@db_operation
def tokensignin(db_session):
    '''On successful Google sign-in, exchange the resulting ID token for the
    user's Google profile info. If the user is not known, they will be
    registered automatically. User ID and profile info are added to the (Flask)
    login session '''
    token_in = request.data
    try:
        id_info = id_token.verify_oauth2_token(
            token_in,
            auth_requests.Request(),
            CLIENT_ID)
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
    '''Sign the user out by deleting their ID and profile info from the (Flask)
    login session '''
    referrer = request.headers.get('Referer') or '/'
    del login_session['user_id']
    del login_session['user_name']
    return redirect(referrer)


# json endpoints
@app.route('/api/v1/cheeses')
@db_operation
def get_cheeses_json(db_session):
    return \
        jsonify(cheeses=[c.serialize for c in get_items(db_session, Cheese)])


@app.route('/api/v1/cheese/<int:cheese_id>')
@db_operation
def get_cheese_json(db_session, cheese_id):
    return jsonify(get_item(db_session, Cheese, id=cheese_id).serialize)


# error handling
@app.errorhandler(400)
def bad_request(e):
    '''Serves a custom template and message in the event of a 400 error '''
    return render_template('400.html', error=e), 400


@app.errorhandler(403)
def unauthorised(e):
    '''Serves a custom template and message in the event of a 403 error '''
    return render_template('403.html', error=e), 403


@app.errorhandler(404)
def item_not_found(e):
    '''Serves a custom template and message in the event of a 404 error '''
    return render_template('404.html', error=e), 404
