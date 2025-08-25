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
    Notification,
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
        validated_data["student"] = user
        validated_data["status"] = "pending"
        application = super().create(validated_data)

        Notification.objects.create(
            recipient=application.thesis.supervisor,
            message=f"{user.username} applied to your thesis '{application.thesis.title}'."
        )

        return application

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

            elif user.role == "supervisor":
                if new_status and new_status not in [
                    Application.Status.ACCEPTED,
                    Application.Status.REJECTED,
                ]:
                    raise serializers.ValidationError("Coordinators can only accept or reject applications.")

            elif new_status:
                raise serializers.ValidationError("You are not allowed to change application status.")

        return attrs

    def update(self, instance, validated_data):
        user = self.context["request"].user
        new_status = validated_data.get("status")

        # Student can only withdraw
        if user.role == "student":
            if new_status != Application.Status.WITHDRAWN:
                raise serializers.ValidationError("Students can only withdraw applications.")

        # Coordinator can accept/reject only for their theses
        elif user.role == "supervisor":
            if instance.thesis.supervisor != user:
                raise serializers.ValidationError("You cannot modify applications for theses you don't own.")
            if new_status not in [Application.Status.ACCEPTED, Application.Status.REJECTED]:
                raise serializers.ValidationError("Coordinators can only accept or reject applications.")

        updated_instance = super().update(instance, validated_data)

        # Create notification for the student
        if user.role == "supervisor" and new_status in [Application.Status.ACCEPTED, Application.Status.REJECTED]:
            Notification.objects.create(
                recipient=instance.student,
                message=f"Your application for '{instance.thesis.title}' was {new_status.lower()}."
            )

        return updated_instance


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
    skill = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Skill.objects.all()
    )

    class Meta:
        model = StudentSkill
        fields = ["id", "student", "skill"]
        read_only_fields = ["id", "student"]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)

class StudentInterestSerializer(serializers.ModelSerializer):
    interest = serializers.SlugRelatedField(
        slug_field="name",
        queryset=ResearchInterest.objects.all()
    )

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

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "recipient", "message", "created_at", "read"]
        read_only_fields = ["id", "recipient", "created_at"]