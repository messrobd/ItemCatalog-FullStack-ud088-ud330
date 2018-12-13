#!/usr/bin/env python3
from flask import \
    Flask, \
    render_template, \
    url_for
from models import \
    Type, \
    Milk, \
    Cheese

app = Flask(__name__)

types = [
    Type(0, 'Blue cheese', 'moldy and good'),
    Type(1, 'Brown cheese', 'fudgy and weird')]
milks = [
    Milk('cow'),
    Milk('goat'),
    Milk('sheep'),
    Milk('buffalo')]
cheeses = [
    Cheese(0, 'stilton', 'Blue cheese', 'cow'),
    Cheese(1, 'gorgonzola', 'Blue cheese', 'cow'),
    Cheese(2, 'roquefort', 'Blue cheese', 'cow'),
    Cheese(3, 'selbu', 'Blue cheese', 'cow'),
    Cheese(4, 'shropshire', 'Blue cheese', 'cow')]
cheeses += [Cheese(5, 'Gudbrandsdalsost', 'Brown cheese', 'goat')]

# page view handlers
@app.route('/')
@app.route('/catalog')
def get_index():
    more_cheese = len(cheeses) > 5
    preview_list = 5 if more_cheese else len(cheeses)
    return render_template('catalog.html', \
        types=types, \
        cheeses=cheeses, \
        preview_list=preview_list, \
        more_cheese=more_cheese)

@app.route('/catalog/type/<int:type_id>')
def get_cheeses(type_id):
    return render_template('cheeses.html', \
        type=types[type_id], \
        cheeses=cheeses)

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
