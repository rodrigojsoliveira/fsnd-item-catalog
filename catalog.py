#!/usr/bin/python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from itemCatalogDatabase_setup import Category
from flask import Flask, render_template, url_for, redirect

engine = create_engine('sqlite:///catalog.db')
Session = sessionmaker(bind=engine)
session = Session()
app = Flask(__name__)

@app.route('/')
def redirectToShowCategories():
    return redirect(url_for('showCategories'))

@app.route('/categories')
def showCategories():
    categories = session.query(Category).all()
    return render_template('categories.html', categories = categories)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)