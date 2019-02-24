from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catacity_database_setup import Base, Category, Item, User

engine = create_engine('postgresql:///catacity')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# ------------ Magical StackOverflow recipe to truncate all tables
#import contextlib
#from sqlalchemy import MetaData
#meta = MetaData()
#with contextlib.closing(engine.connect()) as con:
#    trans = con.begin()
#    for table in reversed(meta.sorted_tables):
#        con.execute(table.delete())
#    trans.commit()
# ------------ End magic, bad magic that is

# TO WIPE ALL DATA FROM DATABASE, USE "psql catacity" AND ENTER:
#     TRUNCATE item, acct, category;

# ----- Add seed data -----
# categories = ['Movies', 'Books', 'Albums']
category1 = Category(id=1, name='Movies')
session.add(category1)
session.commit()

category2 = Category(id=2, name='Books')
session.add(category2)
session.commit()

category3 = Category(id=3, name='Albums')
session.add(category3)
session.commit()

# users = ['Alice', 'Bob']
user1 = User(id=1, name='Alice', email='alice@sample.com')
session.add(user1)
session.commit()

user2 = User(id=2, name='Bob', email='bob@sample.com')
session.add(user2)
session.commit()

# items
item1 = Item(id=1, title='Number 13', description='First movie', category_id=1, user_id=1)

item2 = Item(id=2, title='Woman 2 Woman', description='Second movie', category_id=1, user_id=2)


