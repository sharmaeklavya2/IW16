from django.contrib import admin
from django.contrib.admin import ModelAdmin
from main.models import Question, Player, Answer, GamePerm, RegDetails

class QuestionAdmin(ModelAdmin):
	list_display = ("qno", "title", "score", "corrans", "hint_enabled", "hint_penalty")

class AnswerAdmin(ModelAdmin):
	list_display = ("text", "is_correct", "hint_taken", "user", "time")

class GamePermAdmin(ModelAdmin):
	list_display = ("label", "value")

class PlayerAdmin(ModelAdmin):
	list_display = ("user", "cached_score", "cached_ttime", "ip_address")

class RegDetailsAdmin(ModelAdmin):
	list_display = ("user",) + RegDetails.form_fields

admin.site.register(Question, QuestionAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(GamePerm, GamePermAdmin)
