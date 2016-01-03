# IW16

This is the backend for **Internet Whirlwind 2016**. It is written in Python 3.4 and Django 1.8.

## How to deploy

	python3 manage.py runserver makemigrations
	python3 manage.py runserver migrate
	python3 scripts/add_ques.py data/sample_questions.json
	python3 scripts/set_perms.py
	python3 manage.py createsuperuser
	python3 manage.py runserver 0.0.0.0:8000

## How to test

You can add, remove and edit users, questions, answers, and game permissions using the admin interface at `/admin/`.

You can test the API calls listed in `main/urls.py` using Ajax or curl. You will need to pass the `sessionid` cookie to use the `submit` API call. All API calls are POST and return `text/plain`, except `get_questions` which is GET and returns `application/json`.

API documentation and complete instructions for testing will be added soon.

## Rules of the game

There are multiple questions. All questions have a string as answer. Each user has `MAX_ATTEMPTS` attempts to give a correct answer. Every correct answer gives a single point to the user. There is no negative marking.
