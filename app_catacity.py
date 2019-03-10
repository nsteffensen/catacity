from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy        import create_engine
from sqlalchemy.orm    import sessionmaker
from database_setup    import Base, Category, User, Item   

engine = create_engine('postgresql:///catacity')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

########################################

# This is just a test page for development.  In production, root should map to /categories
@app.route('/')
def route_checklist():
	return render_template('route-checklist.html')

# This is a debug function that just dumps all items in all categories
@app.route('/allitems/')
def showAllItems():
	items = session.query(Item).all()
	return render_template('showAllItems.html', items = items)

#------------------------------------------------------
#  LIST Categories
#------------------------------------------------------
# This is essentially the main page; it lists all categories
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
	return render_template('viewItem.html', category = category, item = item)

#------------------------------------------------------
#  NEW Item
#------------------------------------------------------
@app.route('/category/<int:category_id>/new/', methods=['GET', 'POST'])
def newItem(category_id):
#	return "Test string for: /category/<int:category_id>/new/"
	if request.method == 'POST':
		newItem = Item(title = request.form['title'],
			description = request.form['description'],
			category_id = category_id,
			acct_id = 1) 
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
	if request.method == 'POST':
		if selItem != [] :
			selItem.title = request.form['title']
			selItem.description = request.form['description']
			session.add(selItem)
			session.commit()
			flash("Edited Item: " + selItem.title)
		return redirect(url_for('showAllItems'))
	else:
		category = session.query(Category).filter_by(id = category_id).one()
		return render_template('editItem.html', category = category, item = selItem)


#------------------------------------------------------
#  DELETE Item
#------------------------------------------------------
@app.route('/category/<int:category_id>/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
	deleteItem = session.query(Item).filter_by(id = item_id, category_id = category_id).one()
	if request.method == 'POST':
		if deleteItem != [] :
			session.delete(deleteItem)
			session.commit()
			flash("Deleted item: " + deleteItem.title)
		return redirect(url_for('showItems', category_id = category_id))
	else:
		category = session.query(Category).filter_by(id = category_id).one()
		return render_template('deleteItem.html', category = category, item = deleteItem)


#------------------------------------------------------
#  JSON Endpoint
#------------------------------------------------------
@app.route('/catalog.json/')
def allItemsJson():
#	categories = session.query(Category).all()
#	return jsonify(Categories=[c.serialize for c in categories])

#	items = session.query(Item).all()
#	return jsonify(Items=[i.serialize for i in items])

	categories = session.query(Category).all()
	items = session.query(Item).all()

	for c in categories:
    	Items += c.serialize
    	for i in items:
        	Items += i.serialize  
	return jsonify(Items)




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
	app.secret_key = 'swordfish'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)







