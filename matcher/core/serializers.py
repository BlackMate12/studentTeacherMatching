from rest_framework import serializers
from .models import (
    User,
    Thesis,
    Application,
    Skill,
    ResearchInterest,
    StudentSkill,
    StudentInterest,
    ThesisSkill,
    ThesisInterest,
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "department"]
        read_only_fields = ["id", "role", "email"]

class ThesisSerializer(serializers.ModelSerializer):
    supervisor = UserSerializer(read_only=True)

    class Meta:
        model = Thesis
        fields = [
            "id",
            "title",
            "description",
            "department",
            "keywords",
            "supervisor",
            "status",
            "max_students",
        ]
        read_only_fields = ["id", "supervisor"]

    def create(self, validated_data):
        validated_data["supervisor"] = self.context["request"].user
        return super().create(validated_data)

class ApplicationSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    thesis = serializers.PrimaryKeyRelatedField(queryset=Thesis.objects.all())

    class Meta:
        model = Application
        fields = [
            "id",
            "student",
            "thesis",
            "status",
            "application_date",
            "motivation_letter",
        ]
        read_only_fields = ["id", "student", "application_date"]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        validated_data["status"] = "Pending"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if user.role == "student":
            if validated_data.get("status") != "Withdrawn":
                validated_data.pop("status", None)
        return super().update(instance, validated_data)

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]
        read_only_fields = ["id"]

class ResearchInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchInterest
        fields = ["id", "name"]
        read_only_fields = ["id"]

class StudentSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSkill
        fields = ["id", "student", "skill", "proficiency_level"]
        read_only_fields = ["id", "student"]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)

class StudentInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInterest
        fields = ["id", "student", "interest", "priority"]
        read_only_fields = ["id", "student"]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)

class ThesisSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThesisSkill
        fields = ["id", "thesis", "skill", "required_level"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = self.context["request"].user
        thesis = validated_data["thesis"]
        if thesis.supervisor != user and not user.is_staff:
            raise serializers.ValidationError("You can only add skills to your own theses.")
        return super().create(validated_data)

class ThesisInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThesisInterest
        fields = ["id", "thesis", "interest"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = self.context["request"].user
        thesis = validated_data["thesis"]
        if thesis.supervisor != user and not user.is_staff:
            raise serializers.ValidationError("You can only add interests to your own theses.")
        return super().create(validated_data)