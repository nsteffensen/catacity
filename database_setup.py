import sys

from sqlalchemy                 import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import relationship
from sqlalchemy                 import create_engine

Base = declarative_base()

class Category(Base):
	__tablename__ = 'category'
	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)

	@property
	def serialize(self):
		#Returns object data in easily serializeable format
		return {
			'id'			: self.id,
			'name'			: self.name,
		}	

class User(Base):
	# In PostgreSQL the keyword user is reserved
    __tablename__ = 'acct'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
  
    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'name'         : self.name,
           'email'        : self.email,
       }

class Item(Base):
	__tablename__ = 'item'
	id = Column(Integer, primary_key = True)
	title = Column(String(80), nullable = False)
	description = Column(String(250))
	category_id = Column(Integer, ForeignKey('category.id'))
	category = relationship(Category)
	acct_id = Column(Integer, ForeignKey('acct.id'))
	user = relationship(User)

	@property
	def serialize(self):
		#Returns object data in easily serializeable format
		return {
			'id'			: self.id,
			'title'			: self.title,
			'description'	: self.description,
		}

#------ Must be at end of file:
engine = create_engine('postgresql:///catacity')
Base.metadata.create_all(engine)
