# IW16

This is the backend for **Internet Whirlwind 2016**. It is written in Python 3.4 and Django 1.8. Currently it only includes API calls and admin interface.

API calls are documented in `api_doc.html`. You can find sample data in `/data/`.

## How to set up

	python3 manage.py runserver makemigrations
	python3 manage.py runserver migrate
	python3 scripts/add_ques.py data/sample_qdata.json
	python3 scripts/publicize.py data/sample_qdata.json
	python3 scripts/set_perms.py
	python3 manage.py createsuperuser

## How to test

	python3 manage.py runserver 0.0.0.0:8000

You can then add, remove and edit users, questions, answers, and game permissions using the admin interface at `/admin/`.

## Permissions

It is possible to control if users can register, view questions, answer questions, etc. using game permissions. Game permissions are boolean values. They can be set by running `scripts/set_perms.py`. Currently there are 3 kinds of permissions:

1. `register` - Whether users can register
2. `view_ques` - Whether users can view questions
3. `answer` - Whether users can submit answers to questions
4. `view_ldrbrd` - Whether users can view leaderboard
5. `take_hint` - Whether users can take hint for a question

Game permissions are enforced at API view level. Hence, they do not affect admin interface.

## Rules of the game

There are multiple questions. All questions have a string as answer. All questions have infinite attempts. ACM-ICPC-like rules are used for ranking people.

## Question storage scheme

Questions' text will be in separate HTML files. They will be stored in `/static/ques/`. The filename of the n<sup>th</sup> question will be `n.html`.

All metadata about questions should be stored in a JSON file (`/data/qdata.json` is in `.gitignore`, you can use that). Format of that file should be similar to `data/sample_qdata.json`. Run `scripts/publicize.py` on it to extract the public part from it (that will be put it into `/static/pdata.json` by that script).
