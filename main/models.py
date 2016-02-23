from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

from django.conf import settings

MAX_ANSWER_LENGTH = 30

class Question(models.Model):
	qno = models.PositiveIntegerField("Question number", unique=True)
	corrans = models.CharField("Correct Answer", max_length=MAX_ANSWER_LENGTH)
	score = models.IntegerField()
	hint = models.TextField(blank=True)
	hint_penalty = models.IntegerField(default=0)
	hint_enabled = models.BooleanField()

	def __str__(self):
		return str(self.qno)

class Player(models.Model):
	user = models.OneToOneField(User)
	ip_address = models.GenericIPAddressField()

	contact_fields = ('name1', 'name2', 'email1', 'email2', 'phone1', 'phone2', 'college', 'id1', 'id2')
	name1 = models.CharField(max_length=128)
	name2 = models.CharField(max_length=128, blank=True)
	email1 = models.EmailField()
	email2 = models.EmailField(blank=True)
	phone1 = models.BigIntegerField()
	phone2 = models.BigIntegerField(blank=True, null=True)
	id1 = models.CharField(max_length=30)
	id2 = models.CharField(max_length=30, blank=True)
	college = models.CharField(max_length=100, blank=True)

	cached_score = models.PositiveIntegerField(default=0)
	cached_ttime = models.DurationField(default=timedelta(0))

	def __str__(self):
		return self.user.username
	def get_score(self):
		corrs = Answer.objects.filter(is_correct=True, user=self.user)
		base_score = corrs.aggregate(s=models.Sum('question__score'))["s"] or 0
		hint_penalty = corrs.filter(hint_taken=True).aggregate(s=models.Sum('question__hint_penalty'))["s"] or 0
		return base_score - hint_penalty
	def get_total_time(self):
		corr_answers = list(Answer.objects.filter(is_correct=True, user=self.user))
		return sum((x.get_solve_time() for x in corr_answers), timedelta(0))
	def update_cache(self):
		self.cached_score = self.get_score()
		self.cached_ttime = self.get_total_time()
		self.save()

class Answer(models.Model):
	text = models.CharField("Player's Answer", max_length=MAX_ANSWER_LENGTH, blank=True)
	user = models.ForeignKey(User)
	question = models.ForeignKey(Question)
	is_correct = models.BooleanField(default=False)
	attempts = models.PositiveIntegerField(default=0)
	time = models.DateTimeField()
	hint_taken = models.BooleanField(default=False)

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
	label = models.CharField(max_length=30, unique=True)
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
			player.cached_score+= question.score
			if ans.hint_taken:
				player.cached_score-= question.hint_penalty
			player.cached_ttime+= (time - settings.BASE_DATETIME)
			player.save()
		ans.attempts+= 1
		ans.save()
		return ans
	else:
		return None

def take_hint(question, user):
	"""Returns whether hint can be viewed. Also sets Answer.hint_taken if hint can be viewed"""
	try:
		ans = Answer.objects.get(question=question, user=user)
		if ans.hint_taken:
			return True
	except Answer.DoesNotExist:
		ans = None
	if question.hint_enabled and get_perm("take_hint"):
		if ans==None:
			ans = Answer(question=question, user=user, time=settings.BASE_DATETIME)
		ans.hint_taken = True
		ans.save()
		if ans.is_correct:
			user.player.cached_score-= question.hint_penalty
			user.player.save()
		return True
	else:
		return False
