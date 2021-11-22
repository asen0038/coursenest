from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Course


class Register(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)


class CourseForm(forms.ModelForm):

    class Meta:

        model = Course

        fields = [
            "code",
            "name",
            "description",
        ]
