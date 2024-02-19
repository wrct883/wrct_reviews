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
