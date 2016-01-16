import os
import sys
import getpass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
	sys.path.append(BASE_DIR)

perms = [
	"register",
	"answer",
]

def set_perms():
	for label in perms:
		userin = input("Allow users to {0}? (y/n) ".format(label))
		if userin.lower()=="y":
			value = True
		elif userin.lower()=="n":
			value = False
		else:
			raise ValueError("You must choose y or n")
		try:
			perm = GamePerm.objects.get(label=label)
			perm.value = value
		except GamePerm.DoesNotExist:
			perm = GamePerm(label=label, value=value)
		perm.save()

if __name__=="__main__":
	# set up django
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_conf.settings")
	print("Setting up Django ...", flush=True, end='')
	import django
	django.setup()
	print(" done")

from main.models import Question, Player, GamePerm

if __name__=="__main__":
	set_perms()
