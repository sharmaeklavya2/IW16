from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_safe, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

import json
from datetime import datetime, timedelta

from main.models import Question, Player, Answer, GamePerm, make_answer, get_perm
from django.conf import settings

def TextResponse(message, status=None):
	return HttpResponse(message, content_type="text/plain", status=status)

def MyJsonResponse(object_to_send, status=None):
	return HttpResponse(json.dumps(object_to_send, indent=settings.JSON_INDENT_LEVEL, cls=DjangoJSONEncoder), content_type="application/json", status=status)

def login_required_ajax(func):
	def dec_func(request, **kwargs):
		if request.user.is_authenticated():
			return func(request, **kwargs)
		else:
			return TextResponse("401 - Unauthorized", 401)
	return dec_func

@require_safe
#@login_required_ajax
def get_question(request, qno):
	try:
		qno = int(qno)
		q = Question.objects.get(qno=qno)
		data = settings.DICT_TYPE([("qno", q.qno), ("title", q.title), ("text", q.text)])
		if get_perm("view_ques"):
			return MyJsonResponse(data)
		else:
			return TextResponse("403 - Forbidden - You are not allowed to view questions now", 403)
	except (ValueError, Question.DoesNotExist):
		return TextResponse("404 - Not Found", 404)

@csrf_exempt
@require_POST
def login_view(request):
	if "username" in request.POST and "password" in request.POST and request.POST["username"] and request.POST["password"]:
		user = authenticate(username=request.POST["username"], password=request.POST["password"])
		if not user:
			return TextResponse("wrong_login")
		elif not user.is_active:
			return TextResponse("inactive")
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
	total_time = timedelta(0)
	for ans in corrs_db:
		solve_time = ans.get_solve_time()
		total_time+= solve_time
		corrs.append(get_ans_dict(ans, solve_time))
	wrongs = []
	for ans in wrongs_db:
		wrongs.append(get_ans_dict(ans))
	user_data = [
		("username", user.username),
		("score", len(corrs)),
		("time_taken_s", total_time.total_seconds()),
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
		"base_datetime": settings.BASE_DATETIME,
		"time_penalty_s": settings.TIME_PENALTY_S,
		"perms": perms,
	}
	return MyJsonResponse(response_dict)

@require_safe
def ldrbrd(request):
	response_dict = {}
	if request.user.is_authenticated():
		player = request.user.player
		my_rank = Player.objects.filter(Q(cached_score__gt=player.cached_score) | Q(cached_score=player.cached_score, cached_ttime__lt=player.cached_ttime)).count()+1
		my_page = (my_rank-1)//settings.LDRBRD_PAGE_SIZE
		response_dict["my_rank"] = my_rank
		response_dict["my_page"] = my_page
	qset = Player.objects.filter(cached_score__gt=0).select_related('user').order_by('-cached_score', 'cached_ttime')
	paginator = Paginator(qset, settings.LDRBRD_PAGE_SIZE)
	response_dict["pages"] = paginator.num_pages
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
