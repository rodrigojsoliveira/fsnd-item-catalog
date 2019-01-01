#!/usr/bin/python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from itemCatalogDatabase_setup import Category, Item, Base
from flask import Flask, render_template, url_for, redirect, request, flash

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Session = scoped_session(sessionmaker(bind=engine))
session = Session()

# Redirect all request from root to /categories.
@app.route('/')
def redirectToShowCategories():
    return redirect(url_for('showCategories'))

# Show all categories.
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).all()
    return render_template('categories.html', categories = categories)

# Edit category.
@app.route('/categories/<string:category>/edit/', methods = ['GET', 'POST'])
def editCategory(category):
    category_data = session.query(Category).filter_by(name=category).one()
    if category_data is None:
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        if request.form['name']:
            category_data.name = request.form['name']
            category_data.user_id = request.form['user_id']
            session.add(category_data)
            session.commit()
            flash('Category updated successfuly!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=category_data)

# Show all items in selected category.
@app.route('/categories/<string:category>/items/')
def showItems(category):
    category_data = session.query(Category.id, Category.name).filter_by(name=category).one()
    # Check if category was found. If not, print error message and return to categories page.
    if category_data is None:
        return redirect(url_for('showCategories'))
    items = session.query(Item).filter_by(category_id=category_data[0]).all()
    return render_template('items.html', items=items, category_name = category_data[1])

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)