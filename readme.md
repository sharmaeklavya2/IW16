# IW16

This is the backend for **Internet Whirlwind 2016**. It is written in Python 3.4 and Django 1.8. It has also been tested on Django 1.9. Currently it only includes API calls and admin interface.

API calls are documented in `api_doc.html`. You can find sample data in `/data/`.

## How to set up

	python3 manage.py runserver makemigrations
	python3 manage.py runserver migrate
	python3 scripts/populate.py data/sample_qdata.json
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

There are multiple questions.

1. All questions have a string as answer. Checking is case-insensitive.
2. Infinite attempts are allowed for all questions.
3. Users are first judged by total score and then by total time taken for correctly solved questions.
4. For questions which are eventually correctly solved, each wrong submission will carry a time penalty.
5. Some questions have hints. Each hint has a score penalty if its question is correctly solved.

## Question storage scheme

All data about questions (like correct answer, score, hint, etc) should be stored in a JSON file (`/data/qdata.json` is in `.gitignore`, you can use that). You can look at `data/sample_qdata.json` as an example. Run `scripts/publicize.py` on it to extract the public part from it (that will be put it into `/static/pdata.json` by that script).

Questions' text can either be in the JSON file or in separate HTML files in a folder with the same name as the JSON file except the `.json` extension. Similarly hints can either be in the JSON file or in external HTML files.

This is the order for determining the text of a question:

1. If the question's object in the .json file has a `text` attribute, that attribute's value will be taken as the question's text.
2. If the question's object in the .json file has a `textfile` attribute, that attribute's value will give the name of the file where the question's text is stored.
3. The question's rank along with a .html extension will form the filename which contains the question.
4. The question will not have any text.

This is the order for determining the hint of a question:

1. If the question's object in the .json file has a `hint` attribute, that attribute's value will be taken as the question's hint.
2. If the question's object in the .json file has a `hintfile` attribute, that attribute's value will give the name of the file where the question's text is stored.
3. The question will not have any hint.

## License

IW16 is released under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0).
