from flask import Flask, render_template, request, redirect, jsonify, url_for, flash

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User

import random
import string
import collections

from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from flask import make_response

from dict2xml import dict2xml
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# OAUTH CLIENT_ID GOOGLE

CLIENT_ID = json.loads( open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

# The login and authorization taken from the OAuth Class exercise

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    # OAuth2Credentials object is not JSON serializable error - add the .to_json()
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION - for later use when fb is also added to login
    login_session['provider'] = 'google'

    # see if user exists, if it does'nt make new one
    user_id = getUserID(data['email'])
    if not user_id:
      user_id = createUser(login_session)
    login_session['user_id'] = user_id

    print user_id
    print login_session['username']
    output = ''
    output += '<h1>Welcome, '    
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions
#----------------------

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Disconnect based on provider - TODO FB account
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showMainPage'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showMainPage'))

##########################
#Flask Methods

# Main Page show the Catalog

@app.route('/')
@app.route('/catalog')
def showMainPage():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(CategoryItem).all()
    if 'username' not in login_session:
        return render_template('publicCatalog.html', categories=categories, items=items)
    else:
       return render_template('catalog.html', categories=categories, items=items)


# Show items in each category

@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/item/')
def showItem(category_name):
    category = session.query(Category).filter_by(name=category_name).one()    
    creator = getUserInfo(category.user_id)
    items = session.query(CategoryItem).filter_by(category_id=category.id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicItem.html', items=items, category=category, creator=creator)
    else:
        return render_template('item.html', items=items, category=category, creator=creator)

# Create a new category
#-----------------------

@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
       return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'], image=request.form['image'], user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showMainPage'))
    else:
        return render_template('newCategory.html')

# Edit a category
#------------------

@app.route('/category/<string:category_name>/edit/', methods=['GET', 'POST'])
def editCategory(category_name):
    editedCategory = session.query(
        Category).filter_by(name=category_name).one()
    if 'username' not in login_session:
        return redirect('/login')
        print 'username'
    if editedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this category. Please create your own category in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('showMainPage'))
    else:
        return render_template('editCategory.html', category=editedCategory)

# Delete an existing category
#---------------------------

@app.route('/category/<string:category_name>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_name):
    categoryToDelete = session.query(Category).filter_by(name=category_name).one()    
    if 'username' not in login_session:
      return redirect('/login')
    print categoryToDelete.user_id 
    print login_session['user_id']
    if categoryToDelete.user_id != login_session['user_id']:
      return "<script>function myFunction() {alert('You are not authorized to delete this category.\
             Please create your own category in order to delete.');}\
             </script><bodyonload='myFunction()''>"
      
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showMainPage'))
    else:
        return render_template('deleteCategory.html', category=categoryToDelete)

# Create a new Category item
@app.route('/category/<string:category_name>/item/new/', methods=['GET', 'POST'])
def newCategoryItem(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add  items to this category. Please create your own category in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newItem = CategoryItem(name=request.form['name'], description=request.form['description'], 
                            category_id=category.id, user_id=category.user_id)
        session.add(newItem)
        session.commit()
        flash('New Item %s  Successfully Created' % (newItem.name))                        
        return redirect(url_for('showItem', category_name=category_name))
    else:
        return render_template('newCategoryItem.html', category_name=category_name)

# Edit Category item

@app.route('/category/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
def editCategoryItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(CategoryItem).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(name=category_name).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit items to this category. Please create your own category in order to edit items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']        
        session.add(editedItem)
        session.commit()
        flash('Category Item Successfully Edited')
        return redirect(url_for('showItem', category_name=category_name))
    else:
        return render_template('editCategoryItem.html', category_name=category_name, item_name=item_name, item=editedItem)


# Delete a Category item
@app.route('/category/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteCategoryItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    itemToDelete = session.query(CategoryItem).filter_by(name=item_name).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete items to this category. Please create your own category in order to delete items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Category Item Successfully Deleted')
        return redirect(url_for('showItem', category_name=category_name))
    else:
        return render_template('deleteCategoryItem.html', item=itemToDelete)


#############################################
#Making an API Endpoint (GET Request)
# JSON API ENDPOINT

# JSON APIs to view Catalog Information

#  JSON lists categories with its items

#TODO : get rid of nested loop by modifiying the db (relationship backref) (?)
# http://stackoverflow.com/questions/6179939/python-list-of-dictionaries

@app.route('/catalogbyitems/JSON')
def catalogItemsJSON():  
    categories = session.query(Category).all()
    serializedCategoryItems =[]
    for c in categories:
        serializedCategory = c.serialize
        items = session.query(CategoryItem).filter_by(category_id = c.id).all()
        serializedItems =[]
        for i in items:
            serializedItems.append(i.serialize)
        serializedCategory['items'] = serializedItems
        serializedCategoryItems.append(serializedCategory)
    return jsonify(Category = serializedCategoryItems)
    

# JSON lists all the categories

@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])

# JSON lists all items

@app.route('/allitems/JSON')
def allItemsJSON():
    items = session.query(CategoryItem).all()
    return jsonify(items=[i.serialize for i in items])

# list items of a specific category as specified by the name
# eg: http://localhost:8000/catalog/Soccer/items/JSON

@app.route('/catalog/<string:category_name>/JSON')
def itemByCategoryJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(CategoryItem).filter_by(category_id=category.id).all()
    return jsonify(Category=[category.serialize],Items=[item.serialize for item in items])

############### End JSON ###################

# XML API endpoint

@app.route('/category/XML')
def categoriesXML():
    categories = session.query(Category).all()
    serialCategories =[]
    for c in categories:
        serialCategories.append(c.serialize)
    return dict2xml(serialCategories, wrap='Category', indent='    '), 200, {'Content-Type': 'text/css; charset=utf-8'}
    
@app.route('/allitems/XML')
def allItemsXML():
    items = session.query(CategoryItem).all()
    serialItems =[]
    for item in items:
        serialItems.append(item.serialize)
    return dict2xml(serialItems, wrap='Items', indent='    '), 200, {'Content-Type': 'text/css; charset=utf-8'}    

@app.route('/catalog/<string:category_name>/XML')
def itemByCategoryXML(category_name):
    """ returns an XML"""
    category = session.query(Category).filter_by(name=category_name).one()
    serialCategory = category.serialize
    items = session.query(CategoryItem).filter_by(category_id=category.id).all()
    serialItems =[]
    for item in items:
        serialItems.append(item.serialize)
    serialCategory['items'] = serialItems
    return dict2xml(serialCategory, wrap='Category', indent='    '), 200, {'Content-Type': 'text/css; charset=utf-8'}    
     
      
######################################### 
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)