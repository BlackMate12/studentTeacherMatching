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
        user = self.context["request"].user
        if user.role != "student":
            raise serializers.ValidationError("Only students can create applications.")

        validated_data["student"] = user
        validated_data["status"] = Application.Status.PENDING  # use model enum
        return super().create(validated_data)

    def validate(self, attrs):
        """
        Run role-based permission checks at validation time
        so that serializer.is_valid() fails when inappropriate data is passed.
        """
        user = self.context["request"].user
        new_status = attrs.get("status")

        # Handle UPDATE vs CREATE
        if self.instance:  # updating
            if user.role == "student":
                if self.instance.student != user:
                    raise serializers.ValidationError("You cannot modify another student's application.")
                if new_status and new_status != Application.Status.WITHDRAWN:
                    raise serializers.ValidationError("Students can only withdraw applications.")

            elif user.role == "coordinator":
                if new_status and new_status not in [
                    Application.Status.ACCEPTED,
                    Application.Status.REJECTED,
                ]:
                    raise serializers.ValidationError("Coordinators can only accept or reject applications.")

            elif new_status:
                raise serializers.ValidationError("You are not allowed to change application status.")

        return attrs

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