from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

from django.conf import settings

MAX_ANSWER_LENGTH = 30

class Question(models.Model):
	qno = models.PositiveIntegerField("Question number", unique=True)
	title = models.CharField(max_length=30, blank=True)
	text = models.TextField(blank=True)
	corrans = models.CharField("Correct Answer", max_length=MAX_ANSWER_LENGTH, blank=False)
	score = models.IntegerField(default=0)

	def __str__(self):
		return str(self.qno)+"-"+(self.title or self.text[:30])

class Player(models.Model):
	user = models.OneToOneField(User)
	ip_address = models.GenericIPAddressField()

	contact_fields = ('name1', 'name2', 'email1', 'email2', 'phone1', 'phone2')
	name1 = models.CharField(max_length=128, blank=False)
	name2 = models.CharField(max_length=128, blank=False)
	email1 = models.EmailField(blank=False)
	email2 = models.EmailField(blank=False)
	phone1 = models.BigIntegerField(null=True, blank=True)
	phone2 = models.BigIntegerField(null=True, blank=True)

	cached_score = models.PositiveIntegerField(default=0)
	cached_ttime = models.DurationField(default=timedelta(0))

	def __str__(self):
		return self.user.username
	def get_score(self):
		return Answer.objects.filter(is_correct=True, user=self.user).count()
	def get_total_time(self):
		corr_answers = list(Answer.objects.filter(is_correct=True, user=self.user))
		return sum((x.get_solve_time() for x in corr_answers), timedelta(0))
	def update_cache(self):
		self.cached_score = self.get_score()
		self.cached_ttime = self.get_total_time()
		self.save()

class Answer(models.Model):
	text = models.CharField("Player's Answer", max_length=MAX_ANSWER_LENGTH, blank=False)
	user = models.ForeignKey(User)
	question = models.ForeignKey(Question)
	is_correct = models.BooleanField(default=False)
	attempts = models.PositiveIntegerField(default=0)
	time = models.DateTimeField()

	def __str__(self):
		return "(user={}, question={}, text={}, is_correct={}, attempts={})".format(self.user, self.question, self.text, self.is_correct, self.attempts)
	def get_attstat(self):
		if self.text:
			return self.text.lower()==self.question.corrans.lower()
		else:
			return None
	def get_solve_time(self):
		return (self.time - settings.BASE_DATETIME) + (self.attempts-1)*timedelta(seconds=settings.TIME_PENALTY_S)

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
	if not ans.is_correct:
		player = user.player
		ans.text = userans
		ans.is_correct = ans.get_attstat()
		if ans.is_correct:
			player.cached_score+= 1
			player.cached_ttime+= (time - settings.BASE_DATETIME)
			player.save()
		ans.attempts+= 1
		ans.save()
		return ans
	else:
		return None
