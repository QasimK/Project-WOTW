# Project WOTW

A text-based web adventure game developed using Python with Django.

## Development

### Requirements

* Python 3.4 (some earlier 3.x versions may work)
* Django 1.7.5 (quick install with `pip install django==1.7.5`)

### Getting Started

1. Clone or download the zip.
2. Ensure requirements are fulfilled (e.g. use a [Virtual Environment](https://docs.python.org/3/library/venv.html) & `pip install -r requirements.txt`).
3. Create a fresh game database by running `manage.py resetgame` (enter username/password for an Admin account).
  - Note this can also be used to reset the database with just the *initial game content* at any time.
4. Run `manage.py runserver` and navigate to `127.0.0.1:8000` to play.

### Some notes on the structure of the project

- **/wotw_project/** is the game (Django views, Django database, game code)
- **/wotw_public/** is the Django templates (web-front end).
- `game.models` is split into static and dynamic; the static content is the game content that sets up the game world initially, and the dynamic content is everything else that is created as you play the game. For example, items, shops, monsters, and locations are static content; while characters, inventories, and session data are dynamic content.
- **/wotw\_project/wotw\_database.sqlite3** is the database file which is *not* synced with the repository.
- **/wotw\_project/game/fixtures/initial_fixtures.json** is the fixtures file which holds all of the static game content which can be loaded into the database.

---

`Project WOTW, Copyright © 2010–2015 Qasim K — All Rights Reserved`
