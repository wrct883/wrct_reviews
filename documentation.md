# Documentation

## frontend/backend
Future plans: we need to adapt the backend to work as a Django REST application, and then create a separate React/Typescript frontend.

A separate backend/frontend model (commonly called REST API + frontend, I think) is pretty much what every big tech service does nowadays. A user interacts with a frontend website -- which is going to be built off of HTML/CSS/Javascript. And the frontend makes API calls to the backend, which then fetches information from or manipulates the database, and then returns any relevant data *back* to the frontend as JSON data. The frontend javascript interprets this data and may then display it for the user.

Having a separate backend/frontend for a service allows you to:
* separate work between backend/frontend developers
* allow you to give the frontend a "facelift" without updating the backend views. typicially the frontend works on a faster development cycle than the backend
* make incremental updates to either the backend/frontend, which is easier than just updating the entire service at once
* allow other frontend/command line projects to be created that use the same backend api server

The frontend will make api calls to the backend api endpoints, which will do all the database interactions we need to do: so HTTP GET requests are going to return data, POST requests are going to create database objects, PATCH requests are going to update database items, etc. We'll have to define those backend api endpoints, but the frontend has no idea how that gets implemented. It *just* knows about the url that corresponds to the backend action.

Typically the frontend also uses a *javascript framework* like React or Vue.js. We should use react just bc i have experience with that, lol, but really any of them would work. Using something like react gives you more power when building the frontend and allows you to make "components", which lets you re-use code. There are a ton of other misc benefits too, but that's like, a whole other thing

## a bit about Django
Django is a Python framework that I absolutely love. The fact that I have a favorite python framework doesn't excite me, however. It lets you build Python backends pretty quickly as a lot of the common actions you can do (create/remove/update/destroy-ing database items) can be created in just a few lines.

Ok, so intuitively, programmers create database objects called *model objects*. The django [model fields documentation](https://docs.djangoproject.com/en/5.0/ref/models/fields/) has a ton of information on the specifics of this, but you create *objects* that you store in our database and *fields* that get attached to them. For example, we would track an "Album" as an object, which probably has as fields a name, an artist, a date added, etc. Django takes this code and then formats your SQL database semi-automatically so you can start storing these things.

A django project is divided into `apps` that are just directories. For this project, we have two apps, `accounts` and `library`. `accounts` has information about users, and `library` has information about our music database.

All apps usually have a pretty similar directory structure, which includes
* `models.py` -- where you write your models, what I was talking about above,
* `admin.py` -- which allows you to control what gets displayed on django's admin panel,
* `views.py` -- which creates functions, which is where users can actually do things on your website, or where our API endpoints will be defined,
* `urls.py` -- which connects a view to a URL
* `apps.py` -- usually like, one line, it just defines the name of the app for internal use
* `tests.py` -- you can write functions to test your code here, make sure everything works properly, but I usually ignore this B)

## This repository (currently)
This is the current backend! It creates/manages our database. Django lets you build applications using their templating language, that offer both frontend/backend views, but the majority of this code does "backend" style tasks -- i.e database stuff

* `requirements.txt` - not specific to just Django. every python project is going to have one of these files that says what python packages it uses
    * use `pip install -r requirements.txt` to download packages to your environment
    * use `pip freeze > requirements.txt` to set your packages as the requirements file
* `manage.py` - an executable Django has to perform admin functions / start the server, etc. use like `python3 manage.py <command>`
* `db.sqlite3` - the database file. we use sqlite3 bc it's the django default, but I've seen other services like postgres used as well. it's all SQL though
* `venv/` - the virtual environment directory (if you don't see it you have to create one with `python -m venv venv` and then `source venv/bin/activate`
* `wrct_reviews/` - every django project has another sub-folder that has the same name as the project itself (in this case, `wrct_reviews`). this contains settings for the site (`settings.py`), and passes url configurations to the various apps (`urls.py`)
* `library/` - the library app, which is the bulk of this code, it's where we register all of our music database model objects and define their views, etc
* `accounts/` - stores information about users
