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

# Create new category.
@app.route('/categories/new/', methods = ['GET', 'POST'])
def addCategory():
    if request.method == 'POST':
        # Check if category already exists.
        category = session.query(Category).filter_by(name=request.form['name']).first()
        if category is not None:
            flash('Category already exists.')
            return redirect(url_for('showCategories'))
        else:
            category = Category(name = request.form['name'], user_id = int(request.form['user_id']))
            session.add(category)
            session.commit()
            flash('New category created successfully!')
            return redirect(url_for('showCategories'))
    else:
        return render_template('addCategory.html')

# Edit category.
@app.route('/categories/<string:category>/edit/', methods = ['GET', 'POST'])
def editCategory(category):
    category_data = session.query(Category).filter_by(name=category).first()
    if category_data is None:
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        if request.form['name']:
            category_data.name = request.form['name']
            category_data.user_id = request.form['user_id']
            session.add(category_data)
            session.commit()
            flash('Category updated successfuly!')
        else:
            flash('Nothing changed.')
        return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=category_data)

# Delete empty category.
@app.route('/categories/<string:category>/delete/', methods = ['GET', 'POST'])
def deleteEmptyCategory(category):
    category_data = session.query(Category).filter_by(name=category).first()
    items = session.query(Item).filter_by(category_id=category_data.id).first()
    if category_data is None:
        flash('No such category.')
        return redirect(url_for('showCategories'))
    if items is not None:
        flash('There are items in this category. Unable to delete.')
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        answer = request.form['answer']
        if answer == 'yes':
            session.delete(category_data)
            session.commit()
            flash('Category deleted successfully!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html', category = category_data)        

# Show all items in selected category.
@app.route('/categories/<string:category>/items/')
def showItems(category):
    category_data = session.query(Category.id, Category.name).filter_by(name=category).first()
    # Check if category was found. If not, print error message and return to categories page.
    if category_data is None:
        flash('Category not found.')
        return redirect(url_for('showCategories'))
    items = session.query(Item).filter_by(category_id=category_data[0]).all()
    return render_template('items.html', items=items, category_name = category_data[1])

# Add item.
@app.route('/categories/<string:category>/items/new', methods = ['GET', 'POST'])
def addItem(category):
    category_data = session.query(Category.id, Category.name).filter_by(name=category).first()
    if category_data is None:
        flash('Category not found.')
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        # Check if item already exists.
        item = session.query(Item).filter_by(name=request.form['name']).first()
        if item is not None:
            flash('Item already exists.')
            return redirect(url_for('showItems', category=category))
        name = request.form['name']
        description = request.form['description']
        user_id = request.form['user_id']
        category_id = category_data[0]
        item = Item(name=name, description=description, user_id=user_id, category_id=category_id)
        session.add(item)
        session.commit()
        flash('New item created successfully!')
        return redirect(url_for('showItems', category=category))
    else:
        return render_template('addItem.html', category = category)

# Edit item.

# Delete item.

# Edit user permission level.

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)