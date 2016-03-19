from django import forms
from main.models import RegDetails
from django.contrib.auth.models import User

class RegForm(forms.ModelForm):
	username = forms.CharField(required=True, validators=User._meta.get_field('username').validators)
	password = forms.CharField(required=True, validators=User._meta.get_field('password').validators)
	class Meta:
		model = RegDetails
		fields = RegDetails.form_fields
