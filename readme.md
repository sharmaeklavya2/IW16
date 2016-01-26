# IW16

This is the backend for **Internet Whirlwind 2016**. It is written in Python 3.4 and Django 1.8. Currently it only includes API calls and admin interface.

API calls are documented in `api_doc.html`.

## How to set up

	python3 manage.py runserver makemigrations
	python3 manage.py runserver migrate
	python3 scripts/add_ques.py data/sample_questions.json
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

Game permissions are enforced at API view level. Hence, they do not affect admin interface.

## Rules of the game

There are multiple questions. All questions have a string as answer. All questions have infinite attempts. ACM-ICPC-like rules are used for ranking people.
