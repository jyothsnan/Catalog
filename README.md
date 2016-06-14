# Catalog
Udacity third project, Item Catalog 
Project3 - Item Catalog
-----------------------
Goal -
Develop a web application that provides a list of items within a variety of categories
The web application to be developed in python using the flask framework along with
implementing third-party OAuth authentication

Must Have
----------
1.Vagrant & VirtualBox
2.Clone of fullstack-nanodegree-vm (this installs all the other applications
   required to successfully run - sqlalchemy, flask, sqlite,python etc)
   If you don't have the above, please follow the detailed
		instructions in the Udacity web site -
		https://www.udacity.com/wiki/ud197/install-vagrant
3.To be able to get XML API endpoint, need the library dict2xml (sudo pip install dict2xml)
   
Next -
   
Unzip the file and under Catalog directory you have the following 
static            - directory that contains image files and the css styles.css
template          - this directory has all the html files
database_setup.py - python file that creates the database
lotsofitems.py    - python file that populates the database with initial categories and items
application.py    - the main project file with all the flask methods
catalogwithusers.db - the populated database file



How To
------
Assuming you have all the must haves and after unzipping the file, you are ready to use
log to your virtual machine, launch Vagrant VM (vagrant up)
vagrant ssh
cd to the /vagrant/catalog directory
This directory has pre-complied files ad it is required to show the original database
and the category/items added through the CURD
once in the VM, type python application.py
Then go the chrome browser and go to http://localhost:8000
This should open the home page of the application
If for some reason, port 8000 can not be used, then open the application.py file
and go to the end of the file and in the __main__ modify the port to the available port


Features
---------
1.JSON API endpoints
a. http://localhost:8000/category/JSON - lists all the categories in the database
b. http://localhost:8000/allitems/JSON - lists all the items in the database (items in all categories)
c. http://localhost:8000/catalogbyitems/JSON - superset of a and b; lists all items in each category
d. http://localhost:8000/catalog/Soccer/JSON - lists all the items in the Soccer categroy 
                                               (changing Soccer to any other category name to list it's items)
													
2. XML API endpoints
a.  http://localhost:8000/category/XML - lists all the categories in the database
b.  http://localhost:8000/allitems/XML - lists all the items in the database (items in all categories)
c.  http://localhost:8000/catalog/Soccer/XML - lists all the items in the Soccer categroy 
                                               (changing Soccer to any other category name to list it's items)
(Note: The same piece of code is used for JSON and XML api. So that part of the code can be defined as a function
       and called in each of the endpoint routines. This a code optimization/cleanup that has not been done)
	   
	   
2. Google+ OAuth
3. CRUD operations - User once logged in can 
                          create a new category; When the user creates a new category,
						        along with the name of the category, there is an option
								to provide an image file (link to a image file)
								once the category is successfully created and when in the
								main page, clicking on the newly created category takes you
								to the category page and can see the image by the side of the category name
						  edit the created category; 
						  delete the category
						  Add items to a category (created by the user)
						  Edit items
						  Delete items
						  When the parent (category) is deleted, all the child nodes (items in this case)
                          are deleted too


Testing
-------
Tested on Google Chrome Browser in windows platform
	JSON API endpoints 
	XML API endpoints
	CRUD operations -
		Add a new Category after successfully logging in
			Edit that category; delete the category; 
			add a new item to the category
			delete the category and check if the items are also automatically deleted
		Trying editing a category created by a different user - should not allow you to edit/delete	
		(the initial databse was created with a fake user so as to be able to test the above)
		
The original database is populated with a fake user and 8 categories are created.
The category Tennis is added through the CRUD operations. So are the items in that 
category. After creating this category and it's items, JSON/XML were also checked

Scope for Improvement
---------------------
1. The CSS Styling is one major area of improvement (needs lot of TLC)
2. Edit an item in an Category, option to choose/move to a different category
3. Ability to add/upload pictures to individual items in the category
4. Use email if user name is not present even when a person is logged in
(this feature is from my own experience where I did not have a google+ account (only had gmail)
 and even when I was logged on, the username returned None and hence did not allow me to add items.
 For facilitating debug and development, I went ahead and created the user name in google+.)
5. Add other OAuth2 providers - Facebook, Linkedin etc
6. Add reference links to buy specific items in each category 

The fullstack and OAuth lessons (along with links in instruction notes)
and exercises were of great help. I couldn't have done this project without those lessons.
Also of help were some of the sites listed below -
https://keminglabs.com/print-the-docs-pdfs/1668064.pdf
http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers-contacts-and-friends
Some of the stackoverflow links are provided in the code which were
used to fix some bugs
