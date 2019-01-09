#!/usr/bin/python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from itemCatalogDatabase_setup import Category, Item, Base
from flask import Flask, render_template, url_for, redirect, request, flash, session as login_session
from flask import make_response
import random, string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import requests
import json

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///catalog.db')
Session = scoped_session(sessionmaker(bind=engine))

# Redirect all request from root to /categories.
@app.route('/')
def redirectToShowCategories():
    return redirect(url_for('showCategories'))

# Login
@app.route('/login/')
def userLogin():
    # Create a state token to prevent request forgery.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    # Store state token in user login session.
    login_session['state'] = state
    return render_template('login.html', STATE = state)

@app.route('/gconnect', methods = ['POST'])
def gconnect():
    # Check state token sent from the client, preventing request forgery.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Retrieve one-time-code sent by client. This code was given to the client by Google.
    code = request.data

    # Upgrade the authorization code into a credentials object.
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check with Google if the client's access token is valid.
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % credentials.access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # Abort if there was an error in the access token info.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response #Maybe this line is not necessary.
    
    # Verify that the access token from the client is the same given by Google. 
    # User id and App id must match.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user id doesn't match given user id."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client id doesn't match app's id."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if user is already logged in.
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response #Maybe this line is not necessary.

    # Store the access token for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info.
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    
    # Login successfull. Redirect to categories page.
    flash('Login successfull!')
    return redirect(url_for('showCategories'))

# Disconnect user.
@app.route('/gdisconnect/')
def gdisconnect():
    # Disconnect connected users only.
    credentials = login_session['credentials']
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Send GET request to revoke current token.
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        flash ('Successfully disconnected.')        
        return redirect(url_for('showCategories'))
    else:
        flash ('Failed to revoke token for given user.')        
        return redirect(url_for('showCategories'))

# Show all categories.
@app.route('/categories/')
def showCategories():
    categories = Session.query(Category).all()
    return render_template('categories.html', categories = categories)

# Create new category.
@app.route('/categories/new/', methods = ['GET', 'POST'])
def addCategory():
    if request.method == 'POST':
        # Check if category already exists.
        category = Session.query(Category).filter_by(name=request.form['name']).first()
        if category is not None:
            flash('Category already exists.')
            return redirect(url_for('showCategories'))
        else:
            category = Category(name = request.form['name'], user_id = int(request.form['user_id']))
            Session.add(category)
            Session.commit()
            flash('New category created successfully!')
            return redirect(url_for('showCategories'))
    else:
        return render_template('addCategory.html')

# Edit category.
@app.route('/categories/<string:category>/edit/', methods = ['GET', 'POST'])
def editCategory(category):
    category_data = Session.query(Category).filter_by(name=category).first()
    if category_data is None:
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        if request.form['name']:
            category_data.name = request.form['name']
            category_data.user_id = request.form['user_id']
            Session.add(category_data)
            Session.commit()
            flash('Category updated successfuly!')
        else:
            flash('Nothing changed.')
        return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=category_data)

# Delete empty category.
@app.route('/categories/<string:category>/delete/', methods = ['GET', 'POST'])
def deleteEmptyCategory(category):
    category_data = Session.query(Category).filter_by(name=category).first()
    items = Session.query(Item).filter_by(category_id=category_data.id).first()
    if category_data is None:
        flash('No such category.')
        return redirect(url_for('showCategories'))
    if items is not None:
        flash('There are items in this category. Unable to delete.')
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        answer = request.form['answer']
        if answer == 'yes':
            Session.delete(category_data)
            Session.commit()
            flash('Category deleted successfully!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html', category = category_data)        

# Show all items in selected category.
@app.route('/categories/<string:category>/items/')
def showItems(category):
    category_data = Session.query(Category.id, Category.name).filter_by(name=category).first()
    # Check if category was found. If not, print error message and return to categories page.
    if category_data is None:
        flash('Category not found.')
        return redirect(url_for('showCategories'))
    items = Session.query(Item).filter_by(category_id=category_data[0]).all()
    return render_template('items.html', items=items, category_name = category_data[1])

# Add item.
@app.route('/categories/<string:category>/items/new/', methods = ['GET', 'POST'])
def addItem(category):
    category_data = Session.query(Category.id, Category.name).filter_by(name=category).first()
    if category_data is None:
        flash('Category not found.')
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        # Check if item already exists.
        item = Session.query(Item).filter_by(name=request.form['name']).first()
        if item is not None:
            flash('Item already exists.')
            return redirect(url_for('showItems', category=category))
        if request.form['name']:
            name = request.form['name']
        if request.form['description']:
            description = request.form['description']
        user_id = request.form['user_id']
        category_id = category_data[0]
        item = Item(name=name, description=description, user_id=user_id, category_id=category_id)
        Session.add(item)
        Session.commit()
        flash('New item created successfully!')
        return redirect(url_for('showItems', category=category))
    else:
        return render_template('addItem.html', category = category)

# Edit item.
@app.route('/categories/<string:category>/items/<int:item_id>/edit/', methods = ['GET', 'POST'])
def editItem(category, item_id):
    category_data = Session.query(Category.id, Category.name).filter_by(name=category).first()
    if category_data is None:
        flash('Category not found.')
        return redirect(url_for('showCategories'))
    # Check if item id exists and if it belongs to the selected category.
    item = Session.query(Item).filter_by(id=item_id, category_id=category_data[0]).first()
    if item is None:
        flash('Item does not exist in this category.')
        return redirect(url_for('showItems', category=category))
    if request.method == 'POST':
        # Check if item name already exists in the selected category.
        if item.name == request.form['name']:
            flash('Item already exists in this category.')
            return redirect(url_for('showItems', category = category))
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        item.category_id = category_data[0]
        item.user_id = request.form['user_id']
        Session.add(item)
        Session.commit()
        flash('Item updated successfully!')
        return redirect(url_for('showItems', category=category))
    else:
        return render_template('editItem.html', category = category, item = item)

# Delete item.
@app.route('/categories/<string:category>/items/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteItem(category, item_id):
    category_data = Session.query(Category.id, Category.name).filter_by(name=category).first()
    if category_data is None:
        flash('Category not found.')
        return redirect(url_for('showCategories'))
    # Check if item id exists and if it belongs to the selected category.
    item = Session.query(Item).filter_by(id=item_id, category_id=category_data[0]).first()
    if item is None:
        flash('Item does not exist in this category.')
        return redirect(url_for('showItems', category=category))
    if request.method == 'POST':
        answer = request.form['answer']
        if answer == 'yes':
            Session.delete(item)
            Session.commit()
            flash('Item deleted successfully!')
        return redirect(url_for('showItems', category=category))
    else:
        return render_template('deleteItem.html', category=category, item_id=item_id)

# Edit user permission level.


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)