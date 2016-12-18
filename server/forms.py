from django import forms
from django.contrib.auth.models import User
from server.models import Move
from django.db import models

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'password')

class MoveForm(forms.ModelForm):

    class Meta:
        model = Move
        fields = ('origin', 'target')