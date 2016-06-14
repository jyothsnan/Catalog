from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Category, Base, CategoryItem, User
 
engine = create_engine('sqlite:///catalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Add Categories
category1 = Category(user_id=1, name="Soccer", image="https://bsbproduction.s3.amazonaws.com/portals/6771/images/5th6.jpg")

session.add(category1)
session.commit()
#Add items to the category
categoryItem1 = CategoryItem(user_id=1, name="Cleats", description="Shoe with protusions on the sole", 
                category_id = category1.id)
                      
session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Shin guards", description="Protective pad for the shin",
                category_id = category1.id)
                      
session.add(categoryItem2)
session.commit()

# Next Category and its items
category2 = Category(user_id=1, name="Basketball", image="http://neobasketball.com/img/bballcourt.jpg")

session.add(category2)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Crew Socks",
                             description="Stretchy ribbed socks extending to mid calf",
                             category_id = category2.id)
                      

session.add(categoryItem1)
session.commit()

# category 3
category3 = Category(user_id=1, name="Baseball", 
                     image="http://totalsportscomplex.com/wp-content/uploads/2014/09/baseball-pic.jpg")

session.add(category3)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Crew Socks", 
                            description="Stretchy ribbed socks extending to mid calf",
                            category_id = category3.id)
                      

session.add(categoryItem1)
session.commit()

# category 4
category4 = Category(user_id=1, name="Frisbee", 
                    image="http://uvmbored.com/wp-content/uploads/2015/10/how_the_frisbee_took_flight.jpg")

session.add(category4)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Flying Disc", 
                            description="A Flying disc or a Flying Saucer",
                            category_id = category4.id)
                      

session.add(categoryItem1)
session.commit()

# category 5
category5 = Category(user_id=1, name="Snowboarding", 
  image="https://pantherfile.uwm.edu/collins9/www/finalproject5/Project_5/snowboarding3.jpg")

session.add(category5)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Snowboard", 
                             description="Wooden board suitable to glide on snow",
                             category_id = category5.id)
                      

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Goggles", 
                             description="Anit-glare protective safety glasses",category_id = category5.id)
                      

session.add(categoryItem2)
session.commit()

# category 6
category6 = Category(user_id=1, name="Rock Climbing", image="http://asme.berkeley.edu/wordpress/wp-content/uploads/2013/11/Rock-Climbing-Wallpaper-HD.jpg")

session.add(category6)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Shoes", 
                            description="Superior performance shoew wtih excellent grip", 
                            category_id = category6.id)

                      

session.add(categoryItem1)
session.commit()

# category 7
category7 = Category(user_id=1, name="Skating", image="http://www.ocasia.org/Images-OCA/During-the-Roller-Skating-XXX-contest-between-XXX-_53834132011574.jpg")

session.add(category7)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Skates", 
                             description="Roller skates with bearing suitable for beginner and advanced skater",
                             category_id = category7.id)
                      

session.add(categoryItem1)
session.commit()

# category 8
category8 = Category(user_id=1, name="Hockey", image="http://www.picture-newsletter.com/street-hockey/street-hockey-39.jpg")

session.add(category8)
session.commit()

categoryItem1 = CategoryItem(user_id=1, name="Stick", 
                             description="Composite Stick favorable for both ice and street hockey",
                             category_id = category8.id)
                      

session.add(categoryItem1)
session.commit()


print "added menu items!"