from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

from django.conf import settings

MAX_ANSWER_LENGTH = 30

class Question(models.Model):
	qno = models.PositiveIntegerField("Question number", unique=True)
	title = models.CharField(max_length=30, blank=True)
	text = models.TextField(blank=True)
	image_name = models.CharField(max_length=32, blank=True)
	corrans = models.CharField("Correct Answer", max_length=MAX_ANSWER_LENGTH, blank=False)
	score = models.IntegerField(default=0)

	def __str__(self):
		return str(self.qno)+"-"+(self.title or self.text[:30])

class Player(models.Model):
	user = models.OneToOneField(User)
	ip_address = models.GenericIPAddressField()

	contact_fields = ('name')
	name = models.CharField(max_length=128, blank=False)

	def __str__(self):
		return self.user.username
	def get_qnos_of_attstat(self, attstat):
		return Answer.objects.filter(attstat=attstat).values_list('question__qno', flat=True)
	def get_score(self):
		return Answer.objects.filter(attstat=True).count()

class Answer(models.Model):
	text = models.CharField("Player's Answer", max_length=MAX_ANSWER_LENGTH, blank=False)
	user = models.ForeignKey(User)
	question = models.ForeignKey(Question)
	attstat = models.NullBooleanField("Attempt Status")
	attempts = models.PositiveIntegerField(default=0)
	time = models.DateTimeField()
	# True means correct, False means incorrect, None means not attempted

	def __str__(self):
		return "(user={}, question={}, text={}, attstat={}, attempts={})".format(self.user, self.question, self.text, self.attstat, self.attempts)
	def get_attstat(self):
		if self.text:
			return self.text.lower()==self.question.corrans.lower()
		else:
			return None

class GamePerm(models.Model):
	label = models.CharField(max_length=30, blank=False, unique=True)
	value = models.BooleanField()
	def __str__(self):
		return "({0}, {1})".format(self.label, self.value)

def get_perm(label):
	try:
		return GamePerm.objects.get(label=label).value
	except GamePerm.DoesNotExist:
		return False

def make_answer(question, user, userans):
	time = timezone.now()
	can_answer = get_perm("answer")
	if not (can_answer and userans):
		return None
	try:
		ans = Answer.objects.get(question=question, user=user)
		ans.time = time
	except Answer.DoesNotExist:
		ans = Answer(question=question, user=user, time=time)
	if ans.attempts<settings.MAX_ATTEMPTS and ans.attstat!=True:
		ans.text = userans
		ans.attstat = ans.get_attstat()
		ans.attempts+= 1
		ans.save()
		return ans.attstat
	else:
		return None
