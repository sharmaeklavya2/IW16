from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_safe, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.db.models import Q

import json
from datetime import datetime, timedelta

from main.models import Question, Player, Answer, GamePerm, make_answer, get_perm, take_hint
from django.conf import settings
from main import forms

def TextResponse(message, status=None):
	return HttpResponse(message, content_type="text/plain", status=status)

def MyJsonResponse(object_to_send, status=None):
	return HttpResponse(json.dumps(object_to_send, indent=settings.JSON_INDENT_LEVEL, cls=DjangoJSONEncoder), content_type="application/json", status=status)

def login_required_ajax(func):
	def dec_func(request, **kwargs):
		if not request.user.is_authenticated():
			return TextResponse("401 - Unauthorized", 401)
		elif not Player.objects.filter(user=request.user).exists():
			return TextResponse("403 - You are not a player", 403)
		else:
			return func(request, **kwargs)
	return dec_func

@csrf_exempt
@require_POST
def login_view(request):
	if "username" in request.POST and "password" in request.POST and request.POST["username"] and request.POST["password"]:
		user = authenticate(username=request.POST["username"], password=request.POST["password"])
		if not user:
			return TextResponse("wrong_login")
		elif not user.is_active:
			return TextResponse("inactive", 403)
		else:
			login(request, user)
			return TextResponse("success")
	else:
		return TextResponse("400 - Bad Request - username or password missing", 400)

@csrf_exempt
@require_POST
def logout_view(request):
	logout(request)
	return TextResponse("logged out")

@require_safe
def qno_list(request):
	l = list(Question.objects.values_list('qno', flat=True))
	return MyJsonResponse(l)

@csrf_exempt
@require_POST
@login_required_ajax
def submit(request, qno):
	try:
		qno = int(qno)
		q = Question.objects.get(qno=qno)
		if not get_perm("answer"):
			return TextResponse("403 - Forbidden - You are not allowed to answer questions now", 403)
		elif "answer" in request.POST and request.POST["answer"]:
			ans = make_answer(q, request.user, request.POST["answer"])
			if ans:
				if ans.is_correct:
					attstat = "correct"
				else:
					attstat = "wrong"
				time = ans.time
				solve_time_s = ans.get_solve_time().total_seconds()
			else:
				attstat = "na"
				time = None
				solve_time_s = None
			ans_dict = [
				("attstat", attstat),
				("time", time),
				("solve_time_s", solve_time_s),
			]
			return MyJsonResponse(settings.DICT_TYPE(ans_dict))
		else:
			return TextResponse("400 - Bad Request", 400)
	except (ValueError, Question.DoesNotExist):
		return TextResponse("404 - Not Found", 404)

def get_ans_dict(ans, solve_time=None):
	if solve_time==None:
		solve_time = ans.get_solve_time()
	ans_data = [
		("qno", ans.question.qno),
		("text", ans.text),
		("attempts", ans.attempts),
		("time_taken_s", solve_time.total_seconds()),
		("time", ans.time),
	]
	return settings.DICT_TYPE(ans_data)

@require_safe
@login_required_ajax
def user_info(request):
	user = request.user
	corrs_db = Answer.objects.filter(user=user, is_correct=True)
	wrongs_db = Answer.objects.filter(user=user, is_correct=False, attempts__gt=0)
	corrs = []
	for ans in corrs_db:
		solve_time = ans.get_solve_time()
		corrs.append(get_ans_dict(ans, solve_time))
	wrongs = []
	for ans in wrongs_db:
		wrongs.append(get_ans_dict(ans))
	user_data = [
		("username", user.username),
		("score", user.player.cached_score),
		("time_taken_s", user.player.cached_ttime.total_seconds()),
		("corrects", corrs),
		("wrongs", wrongs),
	]
	user_dict = settings.DICT_TYPE(user_data)
	return MyJsonResponse(user_dict)

@require_safe
def game_info(request):
	perms = {}
	for perm in GamePerm.objects.all():
		perms[perm.label] = perm.value
	response_dict = {
		"total_questions": Question.objects.count(),
		"max_score": Question.objects.aggregate(max_score=models.Sum('score'))["max_score"] or 0,
		"base_datetime": settings.BASE_DATETIME,
		"time_penalty_s": settings.TIME_PENALTY_S,
		"perms": perms,
	}
	return MyJsonResponse(response_dict)

@require_safe
def ldrbrd(request):
	if not get_perm("view_ldrbrd"):
		return TextResponse("ldrbrd_closed", 403)
	response_dict = settings.DICT_TYPE()
	response_dict["page_size"] = settings.LDRBRD_PAGE_SIZE
	qset = Player.objects.filter(cached_score__gt=0).select_related('user').order_by('-cached_score', 'cached_ttime')
	paginator = Paginator(qset, settings.LDRBRD_PAGE_SIZE)
	response_dict["pages"] = paginator.num_pages
	if request.user.is_authenticated():
		try:
			player = request.user.player
			my_rank = Player.objects.filter(Q(cached_score__gt=player.cached_score) | Q(cached_score=player.cached_score, cached_ttime__lt=player.cached_ttime)).count()+1
			my_page = (my_rank-1)//settings.LDRBRD_PAGE_SIZE+1
			response_dict["my_rank"] = my_rank
			response_dict["my_page"] = my_page
		except User.player.RelatedObjectDoesNotExist:
			pass
	page = request.GET.get('page')
	try:
		players = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		players = paginator.page(1)
	except EmptyPage:
		# If page is out of range, deliver last page of results.
		players = paginator.page(paginator.num_pages)
	plist = []
	for p in players:
		plist.append((p.user.username, p.cached_score, p.cached_ttime.total_seconds()))
	response_dict["ldrbrd"] = plist
	return MyJsonResponse(response_dict)

@csrf_exempt
@require_POST
def register(request):
	if not get_perm("register"):
		return TextResponse("reg_closed", 403)

	form = forms.PlayerForm(request.POST)
	if not form.is_valid():
		return TextResponse("invalid_data", 400)

	player = form.save(commit=False)
	username = form.cleaned_data["username"]
	password = form.cleaned_data["password"]
	if User.objects.filter(username=username).exists():
		return TextResponse("username_taken")
	user = User(username=username)
	user.set_password(password)
	user.save()
	user = authenticate(username=username, password=password)
	login(request, user)
	player.user = user
	player.cached_ttime = timedelta(0)
	player.ip_address = request.META["REMOTE_ADDR"]
	player.save()

	return TextResponse("success")

@csrf_exempt
@require_POST
@login_required_ajax
def take_hint_view(request, qno):
	try:
		qno = int(qno)
		q = Question.objects.get(qno=qno)
		can_take_hint = take_hint(q, request.user)
		if can_take_hint:
			return TextResponse(q.hint)
		else:
			return TextResponse("403 - You cannot take hint", 403)
	except (ValueError, Question.DoesNotExist):
		return TextResponse("404 - Not Found", 404)

@require_safe
def hint_status(request, qno):
	try:
		qno = int(qno)
		q = Question.objects.get(qno=qno)
		hint_perm = get_perm("take_hint")
		response_dict = {
			"take_hint_perm": hint_perm,
			"hint_enabled": q.hint_enabled,
		}
		if q.hint_enabled and hint_perm:
			response_dict["hint_penalty"] = q.hint_penalty
		if request.user.is_authenticated():
			try:
				ans = Answer.objects.get(question=q, user=request.user)
				response_dict["hint_taken"] = ans.hint_taken
			except Answer.DoesNotExist:
				response_dict["hint_taken"] = False
		return MyJsonResponse(response_dict)
	except (ValueError, Question.DoesNotExist):
		return TextResponse("404 - Not Found", 404)
