#!/usr/bin/env python3
from flask import \
    Flask, \
    render_template, \
    url_for
from models import \
    Variety, \
    Cheese

app = Flask(__name__)

varieties = [
    Variety(0, 'Blue cheese', 'moldy and good'),
    Variety(1, 'Brown cheese', 'fudgy and weird')]
cheeses = [
    Cheese(0, 'stilton'),
    Cheese(1, 'gorgonzola'),
    Cheese(2, 'roquefort'),
    Cheese(3, 'selbu'),
    Cheese(4, 'shropshire')]
cheeses += [Cheese(5, 'gorgonzola dolce')]

# page view handlers
@app.route('/')
@app.route('/catalog')
def get_index():
    more_cheese = len(cheeses) > 5
    preview_list = 5 if more_cheese else len(cheeses)
    return render_template('catalog.html', \
        varieties=varieties, \
        cheeses=cheeses, \
        preview_list=preview_list, \
        more_cheese=more_cheese)

@app.route('/catalog/variety/<int:variety_id>')
def get_cheeses(variety_id):
    return render_template('cheeses.html', \
    variety=varieties[variety_id], \
    cheeses=cheeses)

@app.route('/catalog/cheese/<int:cheese_id>')
def get_cheese(cheese_id):
    return render_template('cheese.html', cheese=cheeses[cheese_id])

@app.route('/catalog/cheese/new')
def new_cheese():
    return render_template('new_cheese.html')

@app.route('/catalog/cheese/<int:cheese_id>/edit')
def edit_cheese(cheese_id):
    return render_template('edit_cheese.html', cheese=cheeses[cheese_id])

@app.route('/catalog/cheese/<int:cheese_id>/delete')
def delete_cheese(cheese_id):
    return 'delete cheese {}'.format(cheese_id)

@app.route('/login')
def login():
    return 'login'


# start serving
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
