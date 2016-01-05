from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_safe, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder

import json
from collections import OrderedDict

from main.models import Question, Player, make_answer, get_perm
from django.conf import settings

def TextResponse(message, status=None):
	return HttpResponse(message, content_type="text/plain", status=status)

def MyJsonResponse(object_to_send, status=None):
	return HttpResponse(json.dumps(object_to_send, indent=settings.JSON_INDENT_LEVEL, cls=DjangoJSONEncoder), content_type="application/json", status=status)

def login_required_for_api(func):
	def dec_func(request, **kwargs):
		if request.user.is_authenticated():
			return func(request, **kwargs)
		else:
			return TextResponse("401 - Unauthorized", 401)
	return dec_func

@require_safe
#@login_required_for_api
def get_question(request, qno):
	try:
		qno = int(qno)
		q = Question.objects.get(qno=qno)
		data = OrderedDict([("qno", q.qno), ("title", q.title), ("text", q.text)])
		if get_perm("answer"):
			return MyJsonResponse(data)
		else:
			return TextResponse("403 - Forbidden - You are not allowed to view questions now", 403)
	except (ValueError, Question.DoesNotExist):
		return TextResponse("404 - Not Found", 404)

@csrf_exempt
@require_POST
def login_view(request):
	if "uoe" in request.POST and "password" in request.POST and request.POST["uoe"] and request.POST["password"]:
		uoe = request.POST["uoe"]
		password = request.POST["password"]
		try:
			if "@" in uoe:
				username = User.objects.get(email=uoe).username
			else:
				username = uoe
			user = authenticate(username=username, password=password)
		except User.DoesNotExist:
			return TextResponse("wrong_login")
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
@login_required_for_api
def submit(request, qno):
	try:
		qno = int(qno)
		q = Question.objects.get(qno=qno)
		if not get_perm("answer"):
			return TextResponse("403 - Forbidden - You are not allowed to answer questions now", 403)
		elif "answer" in request.POST and request.POST["answer"]:
			attstat = make_answer(q, request.user, request.POST["answer"])
			if attstat==False:
				return TextResponse("wrong")
			elif attstat==True:
				return TextResponse("correct")
			else:
				return TextResponse("na")
		else:
			return TextResponse("400 - Bad Request", 400)
	except (ValueError, Question.DoesNotExist):
		return TextResponse("404 - Not Found", 404)
