from django.conf.urls import url
from main import api_views

urlpatterns = [
#	url(r'^get-question/(?P<qno>\d+)/$', api_views.get_question, name='get_question'),
	url(r'^qno-list/$', api_views.qno_list, name='qno_list'),
	url(r'^login/$', api_views.login_view, name='login'),
	url(r'^logout/$', api_views.logout_view, name='logout'),
	url(r'^submit/(?P<qno>\d+)/$', api_views.submit, name='submit'),
	url(r'^game-info/$', api_views.game_info, name='game_info'),
	url(r'^user-info/$', api_views.user_info, name='user_info'),
	url(r'^ldrbrd/$', api_views.ldrbrd, name='ldrbrd'),
	url(r'^register/$', api_views.register, name='register'),
	url(r'^hint-status/(?P<qno>\d+)/$', api_views.hint_status, name='hint_status'),
	url(r'^take-hint/(?P<qno>\d+)/$', api_views.take_hint_view, name='take_hint'),
]
