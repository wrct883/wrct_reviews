is there some way I can get recent actions? like the Django admin LogEntry, but then display messages like `<user> added <album> to the bin`, or, `<user> moved <album> from TBR to In Bin`?

TODO:
* need a way to dynamically create tables
    * specify fields
    * specify which fields are sortable
    * specify the url parameter used for sorting that table
    * use this in detail view (related albums, related reviews)
    * use this in list views (browse/search)
* remove + update views
* profile page, and profile CRUD views
* list views
* search view
* auth levels per users
* authentication via oauth
* fix the "reviews this semester" thing

# Django Rest API
need to set up api endpoints for:
POST requests
* creating albums
* creating artists
* creating labels
* creating reviews

DELETE requests
* deleting albums
* deleting artists
* deleting labels
* deleting reviews

PUT requests
* updating albums
* updating artists
* updating labels
* updating reviews

GET requests
* listing albums
* listing artists
* listing reviews
* listing labels
    * searching all of these things, too, which would probably be query params
    * ^this would also have to be paginated
* album, artist, review, label detail pages
* user detail pages

## React state
library component
* albums list
    * albums for a given arist
* artists list
    * artist for a given album
* reviews list
    * reviews for a given user
* labels list
    * artists for a given label

auth component
* current user
* users list
