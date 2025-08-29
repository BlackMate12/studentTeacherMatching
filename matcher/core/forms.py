from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Thesis, Application, StudentSkill, StudentInterest, Skill, ResearchInterest


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "role", "department", "password1", "password2"]

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "department"]

class ThesisForm(forms.ModelForm):
    class Meta:
        model = Thesis
        fields = ["title", "description", "department", "interests", "required_skills", "max_students", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "status": forms.Select(),
            "required_skills": forms.CheckboxSelectMultiple(),
            "interests": forms.CheckboxSelectMultiple(),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["motivation_letter"]
        widgets = {"motivation_letter": forms.Textarea(attrs={"rows": 4})}

class StudentSkillForm(forms.ModelForm):
    skill = forms.ModelChoiceField(queryset=Skill.objects.all(), empty_label="Select a skill")
    class Meta:
        model = StudentSkill
        fields = ["skill"]

class StudentInterestForm(forms.ModelForm):
    interest = forms.ModelChoiceField(queryset=ResearchInterest.objects.all(), empty_label="Select an interest")
    priority = forms.ChoiceField(choices=StudentInterest.PRIORITY)
    class Meta:
        model = StudentInterest
        fields = ["interest", "priority"]
