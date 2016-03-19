"""This script deletes all questions from database and reads questions from a JSON file into database"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
	sys.path.append(BASE_DIR)

HINTFILE_ERROR_FORMAT = "Hint not enabled for question {} because file {} was not found"

def add_attrs(obj, attr_list, data, force=True):
	for attr in attr_list:
		if force or attr in data:
			setattr(obj, attr, data[attr])

def add_ques_list(fname):
	Question.objects.all().delete()
	dirname, ext = os.path.splitext(fname)
	with open(fname) as qfile:
		data = json.load(qfile)
		for (i, ques) in enumerate(data):
			q = Question(qno=i+1)
			if "title" in ques:
				print("Adding question:", ques["title"])
			else:
				print("Adding question number", q.qno)
			add_attrs(q, ('score', 'corrans'), ques)
			add_attrs(q, ('title',), ques, False)
			if "hint" in ques:
				add_attrs(q, ('hint', 'hint_penalty'), ques)
				q.hint_enabled = True
			elif "hintfile" in ques:
				hintfname = os.path.join(dirname, ques["hintfile"])
				try:
					ques["hint"] = open(hintfname).read().strip()
					add_attrs(q, ('hint', 'hint_penalty'), ques)
					q.hint_enabled = True
				except OSError:
					q.hint_enabled = False
					print(HINTFILE_ERROR_FORMAT.format(repr(q.title), repr(hintfname)))
			else:
				q.hint_enabled = False
			q.save()

if __name__=="__main__":
	# set up django
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_conf.settings")
	print("Setting up Django ...", flush=True, end='')
	import django
	django.setup()
	print(" done")

from main.models import Question

if __name__=="__main__":
	add_ques_list(sys.argv[1])
