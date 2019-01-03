# ItemCatalog-FullStack-ud088-ud330
Project #2: Item Catalog, of Full Stack Udacity Nanodegree

The system is a web application for viewing and managing items in a catalog.
The following is a summary of the capabilities:
* The front page shows thumbnails of the items, broken down by category
* Clicking on a thumbnail opens the details page for the item
* Logged-in users can perform CRUD operations:
  - Creating a new item is available to any logged-in user via the front page
  - From the details page of an item, edit and delete operations are available
  if the logged-in user is its creator


How to run the application

1. Fork the repo
2. CD into the repo and run 'vagrant up' to bring up the vm
3. 'vagrant ssh' into the vm and cd to /vagrant to access the shared folder
4. run 'python views.py' to start serving (or python3, depending on your environment)
5. browse to localhost:5000 to access the front page


Design

Database

Data is stored in a sqlite database configured via sqlalchemy and accessed from
application code using sqlalchemy ORM. Table definition and other db details
can be found in models.py.

Web server

The web server is implemented using Flask. See views.py for the implementation
of all handlers.

In keeping with sqlalchemy recommendations [1], all handlers that involve
database operations initialise and close their own db session.

State, such as the logged-in user's identity, is maintained using the Flask
session entity (as login_session in my case).  

Pages are rendered using Flask templates, which can be found in the 'templates'
sub-directory.

Form validation is done on the client side using built-in hrml and css features
[4, 5]. Additional validation is done server-side, resulting in 400 errors
handled by Flask errorhandlers  

Authn/Authz

CRUD operations can only be performed by authorized users. Authentication is
performed by Google using their off-the-shelf sign in tool html element [2].

The server does not need to access user data while they are offline, so the
user's identity is passed on successful Google sign-in using the resulting ID
token, per Google recommendations [3].

Sign-out is achieved by deleting the user ID from the login session.

Of necessity, the client_secret file is included in this repo. It is understood
that this is not recommended in practice.

API's

Endpoints are provided to afford read access to a JSON representation of:
1. the full list of items in the catalog
2. an item identified by ID

API access does not require authorisation.


Other files

The repo contains certain other files which are not system components:
* Vagrantfile: configuration for the Vagrant VM (provided by Udacity)
* secret_key_generator.py: a script for generating the secret key used to sign
the Flask login session



References:
  1. https://docs.sqlalchemy.org/en/rel_1_2/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it
  2. https://developers.google.com/identity/sign-in/web/sign-in
  3. https://developers.google.com/identity/sign-in/web/backend-auth
  4. https://www.the-art-of-web.com/html/html5-form-validation/
  5. https://stackoverflow.com/questions/9707021/how-do-i-auto-hide-placeholder-text-upon-focus-using-css-or-jquery
