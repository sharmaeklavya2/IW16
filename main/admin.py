from django.contrib import admin
from django.contrib.admin import ModelAdmin
from main.models import Question, Player, Answer, GamePerm

class QuestionAdmin(ModelAdmin):
	list_display = ("qno", "title", "corrans")

class AnswerAdmin(ModelAdmin):
	list_display = ("text", "is_correct", "user", "time")

class GamePermAdmin(ModelAdmin):
	list_display = ("label", "value")

admin.site.register(Question, QuestionAdmin)
admin.site.register(Player)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(GamePerm, GamePermAdmin)
