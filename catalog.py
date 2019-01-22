#!/usr/bin/python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from itemCatalogDatabase_setup import Category, Item, Base, User
from flask import Flask, render_template, url_for, redirect, request, flash, session as login_session
from flask import make_response, jsonify
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

    # Check with Google client's access token.
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

    # Get user info from Google.
    userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # Check if user exists in database. If not, create a new user.
    existingUser = getUserID(login_session['email'])
    if existingUser is None:
        user_id = createUser(login_session)
        newUser = getUser(user_id)
        flash('Hello, %s! This is your first access.' % newUser.username)
    else:
        returningUser = getUser(existingUser)
        user_id = returningUser.id
        flash('Welcome back, %s' % returningUser.username)

    # Login successfull. Add user_id to login_session and redirect to categories page.
    login_session['user_id'] = user_id
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
        del login_session['user_id']
        flash ('Successfully disconnected.')        
        return redirect(url_for('showCategories'))
    else:
        flash ('Failed to revoke token for given user.')        
        return redirect(url_for('showCategories'))

# Show all categories.
@app.route('/categories/')
def showCategories():
    categories = Session.query(Category).all()
    if ('username') not in login_session:
        return render_template('items.html', categories = categories)
    else:
        return render_template('items_editable.html', categories = categories)

# Show all items in selected category.
@app.route('/categories/<string:category>/items/')
def showItems(category):
    category_data = Session.query(Category.id, Category.name).filter_by(name=category).first()
    categories = Session.query(Category).all() #linha nova
    # Check if category was found. If not, print error message and return to categories page.
    if category_data is None:
        flash('Category not found.')
        return redirect(url_for('showCategories'))
    items = Session.query(Item).filter_by(category_id=category_data[0]).all()
    # If user is not logged in, show item list only, without edit capabilities.
    if ('username') not in login_session:
        return render_template('items.html', categories = categories, items=items, category_name=category_data[1]) #linha nova
        #return render_template('items.html', items=items, category_name=category_data[1])
    else:
        return render_template('items_editable.html', categories = categories, items = items, category_name = category_data[1], user_id = login_session['user_id'])

# Add item.
@app.route('/categories/<string:category>/items/new/', methods = ['GET', 'POST'])
def addItem(category):
    if 'username' not in login_session:
        return redirect(url_for('userLogin'))
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
        user_id = login_session['user_id']
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
    if 'username' not in login_session:
        return redirect(url_for('userLogin'))
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
        Session.add(item)
        Session.commit()
        flash('Item updated successfully!')
        return redirect(url_for('showItems', category=category))
    else:
        return render_template('editItem.html', category = category, item = item)

# Delete item.
@app.route('/categories/<string:category>/items/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteItem(category, item_id):
    if 'username' not in login_session:
        return redirect(url_for('userLogin'))
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

# *** API endpoints ***
# Return all categories.
@app.route('/json/categories/')
def getCategories():
    categories = Session.query(Category).all()
    return jsonify(Categories = [c.serialize for c in categories])

# Return all items.
@app.route('/json/items/')
def getItems():
    items = Session.query(Item).all()
    return jsonify(Items = [i.serialize for i in items])

# Return all items in specified category.
@app.route('/json/<string:category>/items/')
def getItemsFromCategory(category):
    category_id = Session.query(Category.id).filter_by(name=category).first()
    print(category_id)
    if category_id is not None:
        items = Session.query(Item).filter_by(category_id=category_id[0]).all()
        return jsonify(Items = [i.serialize for i in items])
    else:
        return ('Category not found.')

# Creates a new user if its his/her first login and return their user_id.
def createUser(login_session):
    newUser = User(username = login_session['username'], email = login_session['email'])
    Session.add(newUser)
    Session.commit()
    # Retrieve new user's user_id
    user_id = Session.query(User).filter_by(email = login_session['email']).one()
    return user_id

# Return a User object based on their user_id.
def getUser(user_id):
    user = Session.query(User).filter_by(id = user_id).one()
    return user

# Retrieve a user_id based on their email.
def getUserID(email):
    user = Session.query(User).filter_by(email = email).first()
    if user:
        return user.id
    else:
        return None

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)