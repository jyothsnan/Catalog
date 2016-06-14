from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

#class definition
class User(Base):
  # table info
    __tablename__ = 'user'
   # mapper info
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

#class definition
class Category(Base):
  # table info
    __tablename__ = 'category'
   # mapper info
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    image = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User) #relationship("User", cascade="save-update")
    items = relationship('CategoryItem', backref="category", cascade="all, delete-orphan", lazy='dynamic') 
    #http://docs.sqlalchemy.org/en/improve_toc/orm/cascades.html
    #http://techarena51.com/index.php/one-to-many-relationships-with-flask-sqlalchemy/

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
           
       }

#class definition    
class CategoryItem(Base):
  # table info
    __tablename__ = 'category_item'

    # mapper info
    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(500))
    category_id = Column(Integer,ForeignKey('category.id')) #many to one
    #category = relationship(Category,backref=backref("items",cascade="all, delete")) #http://stackoverflow.com/questions/5033547/sqlachemy-cascade-delete
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User) #relationship("User", cascade="save-update")


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {    
           'name'         : self.name,      
           'id'         : self.id,   
           'description'         : self.description, 
       }


engine = create_engine('sqlite:///catalogwithusers.db', echo=True)
 

Base.metadata.create_all(engine)
