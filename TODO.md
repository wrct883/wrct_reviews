
TODO:
* need a way to dynamically create tables
    * specify fields - DONE
    * specify which fields are sortable
    * specify the url parameter used for sorting that table
    * use this in detail view (related albums, related reviews) - DONE
    * use this in list views (browse/search) - DONE
* "explore bin" view
    * and bring back "tools" a la olddb
* profile page, and profile CRUD views
* review leaderboard view
* auth levels per users
    * permission: only admin can make another user an admin, only exec can make another user exec, etc
* authentication via oauth
* bin actions: like the Django admin LogEntry, but then display messages like `<user> added <album> to the bin`, or, `<user> moved <album> from TBR to In Bin`?

* fix the "reviews this semester" thing
* need pagination on "related albums" tables
* make subgenres only show whatever genre is selected (need to modify genre select and subgenre widgets)

* add links to listen to an album on spotify/apple music?
    * holy shit, can we integrate this with the spinitron api to get play data on albums/artists on our site??
* add an api call to get album art?
* add autocomplete on create search

looks:
* messages css
* put the `edit links` as its own sidepanel
* add the little icons from the old bin back to the edit links, I liked those
* for `comment` and `review` labels, add my own css to those

* set `date_removed` when updating an item from the bin, to not be in the bin

spinitron integration??
* creating a user automatically creates a spinitron user?
* you can view artist spins on the artist detail page
* you can view album spins on the album detail page
    * also do album art

## 2024-08-14
* library tables: review, album, artist, label, genre
* accounts: profile
* title on detail views
* idea: spotify links on the profile page

DONE:
* search view

hours: call it at least 3

## 2024-08-15
* on the create page, you should see a searchable select field for everything *but* the related table field, if provided

DONE:
* progress on custom select field for searching
* modified search view to produce json, and hooked up the search input field to hit that endpoint on keypress (debounced ofc)


# 2024-08-16
DONE:
* think I largely finished the searching on create, maybe add autocomplete next
* update view (mostly) done
* delete view done

* moved accounts to be under library
* add subgenres which are many to many
    * make genre back to a foreign key again methinks

---
# todo i made for chris

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
