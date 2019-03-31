from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy        import create_engine
from sqlalchemy.orm    import sessionmaker
from database_setup    import Base, Category, User, Item   

# Imports for anti-forgery state token
from flask import session as login_session # "session" already used for db
import random, string

# Imports for OAuth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests  # improved over urllib2
import json
from flask import make_response

#auth = HTTPBasicAuth()
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


engine = create_engine('postgresql:///catacity')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#       #######  #####    ###   #     #
#       #     # #     #    #    ##    #
#       #     # #          #    # #   #
#       #     # #  ####    #    #  #  #
#       #     # #     #    #    #   # #
#       #     # #     #    #    #    ##
####### #######  #####    ###   #     #

#------------------------------------------------------
#  Login
#------------------------------------------------------
@app.route('/login')
def showLogin():
	if 'username' not in login_session:
		# Create anti-forgery state token
		state = ''.join(random.choice(
			string.ascii_uppercase + string.digits) for x in xrange(32))
		login_session['state'] = state
		return render_template('login.html', STATE=state)
	else:
		return render_template('logout.html')


 #####  ####### #######  #####  #       #######
#     # #     # #     # #     # #       #
#       #     # #     # #       #       #
#  #### #     # #     # #  #### #       #####
#     # #     # #     # #     # #       #
#     # #     # #     # #     # #       #
 #####  ####### #######  #####  ####### #######

#------------------------------------------------------
#  Google OAuth2
#------------------------------------------------------
@app.route('/gconnect', methods=['POST'])
def gconnect():
  # Bail if the session token is not right; might be a CSRF attack.
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state token'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
 
  code = request.data  # This is the one-time use code from Google via client

  # Upgrade the authorization code into a credentials object
  try:
    oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code) # exchanges auth code for credentials object
  except FlowExchangeError:
    response = make_response(json.dumps('Failed to upgrade the auth code.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Verify access token is valid by sending it to Google for a check
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
    % access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])

  # If there was an error in the access token info, abort.
  if result.get('error') is not None:
    response = make_response(json.dumps(result.get('error')), 500) 
    response.headers['Content-Type'] = 'application/json'
    return response

  #Verify that the access token is for the intended user
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
    response = make_response(json.dumps(
      "Token UserID does not match given UserID"), 401) 
    response.headers['Content-Type'] = 'application/json'
    return response

  # Verify that the access token is valid for this app.
  if result['issued_to'] != CLIENT_ID:
    response = make_response(json.dumps("Token ClientID does not match this app"), 401)
    print "Token's client ID does not match this app."
    response.headers['Content-Type'] = 'application/json'
    return response

  # Check if user is already logged in 
  stored_credentials = login_session.get('credentials')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_credentials is not None and gplus_id == stored_gplus_id:
    response = make_response(json.dumps("User is already logged in."), 200)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Passed all checks!

  # Get User info
  userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
  params = {'access_token': credentials.access_token, 'alt':'json'}
  answer = requests.get(userinfo_url, params=params)
  data = json.loads(answer.text)
  # "data" now contains all info listed in Google's getOpenIdConnect response

  # Store the access token in the session for later use.
  login_session['provider'] = 'google'
  login_session['access_token'] = credentials.access_token
  login_session['gplus_id'] = gplus_id
  login_session['username'] = data["name"]
  login_session['picture'] = data["picture"]
  login_session['email'] = data["email"]

  # see if user exists, if not then create
  user_id = getUserID(login_session['email'])
  if not user_id:
  	user_id = createUser(login_session)
  login_session['user_id'] = user_id

  test =  '<p>Username: ' + login_session['username'] + '</p>'
  test += '<p>Email: '    + login_session['email'] + '</p>'
  test += '<p>Picture: '  + login_session['picture'] + '</p>'
  test += '<p>User ID: '  + str(login_session['user_id']) + '</p>'
  flash("You are now logged in as %s" %login_session['username'])
  return test



                ##############
                ##          ##
                ##          ##
                ##          ##
                ##          ##
            ######          ######
              ##              ##
                ##          ##
                  ##      ##
                    ##  ##
                      ##


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route("/gdisconnect")
def gdisconnect():
  # Only disconnect a connected user.
  access_token = login_session.get('access_token')
  if access_token is None:
    response = make_response(json.dumps('Current user not connected.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Execute HTTP GET request to revoke current token
  r = requests.post('https://accounts.google.com/o/oauth2/revoke',
    params={'token': access_token},
    headers = {'content-type': 'application/x-www-form-urlencoded'})
  # From Google:
    # Note: Following a successful revocation response,
    # it might take some time before the revocation has full effect.

  del login_session['access_token']
  del login_session['gplus_id']
  del login_session['username']
  del login_session['email']
  del login_session['picture']
  #response = make_response(json.dumps('Successfully disconnected.'), 200)
  #response.headers['Content-Type'] = 'application/json'
  flash("Successfully logged out.")
  return redirect("/", code=302)


########################################
# Debug pages
@app.route('/test')
def route_checklist():
	return render_template('route-checklist.html')

@app.route('/allitems/')
def showAllItems():
	items = session.query(Item).all()
	return render_template('showAllItems.html', items = items)

@app.route('/state')
def showState():
	state = ''.join(random.choice(
		string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return "Session state: %s" %login_session['state']
########################################

#     #   ###   ####### #     #
#     #    #    #       #  #  #
#     #    #    #       #  #  #
#     #    #    #####   #  #  #
 #   #     #    #       #  #  #
  # #      #    #       #  #  #
   #      ###   #######  ## ##

#------------------------------------------------------
#  LIST Categories
#------------------------------------------------------
# This is essentially the main page; it lists all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
	categories = session.query(Category).all()
	return render_template('showCategories.html', categories = categories)

#------------------------------------------------------
#  LIST Category:Items
#------------------------------------------------------
@app.route('/category/<int:category_id>/')
def showItems(category_id):
	category = session.query(Category).filter_by(id = category_id).one()
	items = session.query(Item).filter_by(category_id = category_id).all()
	return render_template('showItems.html', category = category, items = items)

#------------------------------------------------------
#  VIEW Item
#------------------------------------------------------
@app.route('/category/<int:category_id>/item/<int:item_id>')
def viewItem(category_id, item_id):
	category = session.query(Category).filter_by(id = category_id).one()
	item = session.query(Item).filter_by(id = item_id, category_id = category_id).one()
	if 'username' not in login_session or item.acct_id != login_session['user_id']:
		return render_template('publicViewItem.html', category = category, item = item)
	#if 'username' not in login_session:# or item.acct_id != login_session['user_id']:
	#	return render_template('publicViewItem.html', category = category, item = item)
	#elif item.acct_id != login_session['user_id']:
	#	return render_template('publicViewItem.html', category = category, item = item)
	else:
		return render_template('viewItem.html', category = category, item = item)

#------------------------------------------------------
#  VIEW All of My Items
#------------------------------------------------------
@app.route('/myitems/')
def showMyItems():
	items = session.query(Item).filter_by(acct_id = login_session['user_id']).all()
	return render_template('showMyItems.html', items = items)


####### ######    ###   #######
#       #     #    #       #
#       #     #    #       #
#####   #     #    #       #
#       #     #    #       #
#       #     #    #       #
####### ######    ###      #

#------------------------------------------------------
#  NEW Item
#------------------------------------------------------
@app.route('/category/<int:category_id>/new/', methods=['GET', 'POST'])
def newItem(category_id):
#	return "Test string for: /category/<int:category_id>/new/"
	if 'username' not in login_session:
		return redirect('/login')
	if request.method == 'POST':
		newItem = Item(title = request.form['title'],
			description = request.form['description'],
			category_id = category_id,
			acct_id = login_session['user_id']) 
#TODO: replace account_id value with the authenticated user_id		
		session.add(newItem)
		session.commit()
		flash("Created new item: " + newItem.title)
		return redirect(url_for('showAllItems'))
#TODO: replace with showItems with the category indicated somehow
	else:
		category = session.query(Category).filter_by(id = category_id).one()
		return render_template('newItem.html', category = category)

#------------------------------------------------------
#  EDIT Item
#------------------------------------------------------
@app.route('/category/<int:category_id>/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(category_id, item_id):
#	return "Test string for: /category/<int:category_id>/item/<int:item_id>/edit/"
	selItem = session.query(Item).filter_by(id = item_id, category_id = category_id).one()

	#if selItem.id != login_session['user_id']:
	#	test += '<p>Item: '  + login_session['picture'] + '</p>'
	#	test += '<p>User ID: '  + str(login_session['user_id']) + '</p>'
  	#	return test

	if 'username' not in login_session or selItem.acct_id != login_session['user_id']:
		return redirect('/login')

	if request.method == 'POST':
		if selItem != [] :
			selItem.title = request.form['title']
			selItem.description = request.form['description']
			selItem.category_id = request.form.get('category_select')
			session.add(selItem)
			session.commit()
			flash("Edited Item: " + selItem.title)
		return redirect(url_for('showAllItems'))
	else:
		category = session.query(Category).filter_by(id = category_id).one()
		categories = session.query(Category).all()
		return render_template('editItem.html', categories = categories, category = category, item = selItem)


#------------------------------------------------------
#  DELETE Item
#------------------------------------------------------
@app.route('/category/<int:category_id>/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
	deleteItem = session.query(Item).filter_by(id = item_id, category_id = category_id).one()

	if 'username' not in login_session or deleteItem.acct_id != login_session['user_id']:
		return redirect('/login')

	if request.method == 'POST':
		if deleteItem != [] :
			session.delete(deleteItem)
			session.commit()
			flash("Deleted item: " + deleteItem.title)
		return redirect(url_for('showItems', category_id = category_id))
	else:
		category = session.query(Category).filter_by(id = category_id).one()
		return render_template('deleteItem.html', category = category, item = deleteItem)


######  ####### ######  #     #   ###    #####   #####    ###   ####### #     #
#     # #       #     # ##   ##    #    #     # #     #    #    #     # ##    #
#     # #       #     # # # # #    #    #       #          #    #     # # #   #
######  #####   ######  #  #  #    #     #####   #####     #    #     # #  #  #
#       #       #   #   #     #    #          #       #    #    #     # #   # #
#       #       #    #  #     #    #    #     # #     #    #    #     # #    ##
#       ####### #     # #     #   ###    #####   #####    ###   ####### #     #

#------------------------------------------------------
#  Permissions System
#------------------------------------------------------
def createUser(login_session):
	newUser = User(name = login_session['username'],
		email = login_session['email'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email = login_session['email']).one()
	return user.id

def getUserID(email):
	try:
		user = session.query(User).filter_by(email = email).one()
		return user.id
	except:
		return None

def getUserInfo(user_id):
	user = session.query(User).filter_by(id = user_id).one()
	return user


      #  #####  ####### #     #
      # #     # #     # ##    #
      # #       #     # # #   #
      #  #####  #     # #  #  #
#     #       # #     # #   # #
#     # #     # #     # #    ##
 #####   #####  ####### #     #

#------------------------------------------------------
#  JSON Endpoint
#------------------------------------------------------
@app.route('/catalog.json/')
def allItemsJson():
	categories = session.query(Category).all()  # List of objects
	CategoryList = [c.serialize for c in categories] #List of dicts
	for cl in CategoryList:  # Single dict
		items = session.query(Item).filter_by(category_id = cl['id']).all()
		ItemList = [i.serialize for i in items] # List of dicts
		cl['items'] = ItemList  # Append List of item dicts to this Cat dict
	return jsonify(CategoryList) # Convert List of dicts to JSON

@app.route('/category/<int:category_id>/item/<int:item_id>/json/')
def itemJson(category_id, item_id):
	item = session.query(Item).filter_by(id=item_id, category_id=category_id).one()
	if item != [] :
		return jsonify(item.serialize)
	else:
		return "Item not found in database."

#------------------------------------------------------
#  Invoke when main
#------------------------------------------------------
if __name__ == '__main__':
	app.secret_key = 'swordfish'  # Needed for sessions for flash msgs
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)







