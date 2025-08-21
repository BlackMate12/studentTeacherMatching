from rest_framework import serializers
from .models import User, Thesis, Application, Skill, ResearchInterest, StudentInterest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "department"]

class ThesisSerializer(serializers.ModelSerializer):
    supervisor = UserSerializer(read_only=True)

    class Meta:
        model = Thesis
        fields = ["id", "title", "description", "department", "keywords",
                  "supervisor", "status", "max_students"]

class ApplicationSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    thesis = ThesisSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ["id", "student", "thesis", "status", "application_date", "motivation_letter"]

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]

class ResearchInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchInterest
        fields = ["id", "name"]

class StudentInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInterest
        fields = ["id", "student", "interest", "priority"]
