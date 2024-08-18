
TODO:
* auth levels per users
    * permission: only admin can make another user an admin, only exec can make another user exec, etc
* authentication via oauth

* add autocomplete on create search

* bulk actions? just bulk delete, really
* "add another `table` like this function" - editing link

looks:
* add the little icons from the old bin back to the edit links, I liked those

* set `date_removed` when updating an item from the bin, to not be in the bin

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

# 2024-08-17
DONE:
* bin action log

DONE:
* explore bin view
* review leaderboard view

DONE:
* dynamic, sortable, includable tables finally finished :))

DONE:
* subgenre filtering using js
* album art / last fm data on album page
* media queries
* "add a subgenre for this album" - editing link

NEXT:
* auth level permissions (only admin can make admin, etc)
* auth
* deploy


wrct db
API key 	8c96e05d82dcc8bd73ad54b96dd26c25
Shared secret 	2f0b39da6295da2f14793521add274a3
Registered to 	wrct883fm

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
