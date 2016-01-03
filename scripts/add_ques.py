import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
	sys.path.append(BASE_DIR)

def add_ques_list(fname):
	Question.objects.all().delete()
	with open(fname) as qfile:
		data = json.load(qfile)
	for (i, ques) in enumerate(data):
		Question(qno=i+1, **ques).save()

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
