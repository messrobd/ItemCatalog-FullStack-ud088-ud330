#!/usr/bin/env python3
from flask import \
    Flask, \
    render_template

app = Flask(__name__)

varieties = ['Blue cheese', 'Brown cheese']
cheeses = ['stilton', 'gorgonzola', 'roquefort', 'selbu', 'shropshire']
#cheeses = ['stilton']

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
    return 'cheeses of variety {}'.format(variety_id)

@app.route('/catalog/cheese/<int:cheese_id>')
def get_cheese(cheese_id):
    return 'cheese {}'.format(cheese_id)

@app.route('/catalog/cheese/new')
def new_cheese():
    return 'new cheese'

@app.route('/catalog/cheese/edit/<int:cheese_id>')
def edit_cheese(cheese_id):
    return 'edit cheese {}'.format(cheese_id)

@app.route('/catalog/cheese/delete/<int:cheese_id>')
def delete_cheese(cheese_id):
    return 'delete cheese {}'.format(cheese_id)

@app.route('/login')
def login():
    return 'login'


# start serving
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
