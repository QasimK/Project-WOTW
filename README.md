# Project WOTW

A text-based web adventure game developed using Python with Django.

## Development

### Requirements

* Python 3.4 (some earlier 3.x versions may work)
* Django 1.7.5 (quick install with `pip install django==1.7.5`)

### Getting Started

1. Clone or download the zip.
2. Ensure requirements are fulfilled (e.g. use a Virtual Environment & `pip install -r requirements.txt`).
3. Create a fresh game database by running `load_content_fixture.py` and set up the admin account (e.g. `admin`;`password`).
4. Run `manage.py runserver` and navigate to `127.0.0.1:8000` to play.

### Some notes on the structure of the project

- **/wotw_project/** is the game (Django views, Django database, game code)
- **/wotw_public/** is the Django templates (web-front end).
- `game.models` is split into static and dynamic; the static content is the game content that sets up the game world initially, and the dynamic content is everything else that is created as you play the game.

---

`Project WOTW, Copyright © 2010–2015 Qasim K — All Rights Reserved`
