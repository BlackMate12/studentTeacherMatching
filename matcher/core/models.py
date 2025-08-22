from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        SUPERVISOR = "supervisor", "Supervisor"

    role = models.CharField(max_length=20, choices=Role.choices)
    department = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Skill(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name

class ResearchInterest(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name

class Thesis(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ASSIGNED = "assigned", "Assigned"
        CLOSED = "closed", "Closed"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department = models.CharField(max_length=120, blank=True)
    keywords = models.CharField(max_length=300, blank=True)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='theses',
                                   limit_choices_to={'role': User.Role.SUPERVISOR})
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    max_students = models.PositiveIntegerField(default=1)

    interests = models.ManyToManyField(ResearchInterest, through='ThesisInterest', related_name='theses')
    required_skills = models.ManyToManyField(Skill, through='ThesisSkill', related_name='theses')

    def __str__(self):
        return f"{self.title} ({self.supervisor.username})"

    @property
    def current_assigned_count(self):
        return self.applications.filter(status=Application.Status.ACCEPTED).count()

    @property
    def has_capacity(self):
        return self.current_assigned_count < self.max_students

class Application(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications',
                                limit_choices_to={'role': User.Role.STUDENT})
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    application_date = models.DateTimeField(default=timezone.now)
    motivation_letter = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'thesis')

    def __str__(self):
        return f"App({self.student.username} -> {self.thesis.title}) [{self.status}]"

class StudentSkill(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_skills',
                                limit_choices_to={'role': User.Role.STUDENT})
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    #proficiency_level = models.PositiveIntegerField(null=True, blank=True)  # 1-5 (optional)

    class Meta:
        unique_together = ('student', 'skill')


class StudentInterest(models.Model):
    PRIORITY = (
        (1, "Low"),
        (2, "Medium"),
        (3, "High"),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_interests',
                                limit_choices_to={'role': User.Role.STUDENT})
    interest = models.ForeignKey(ResearchInterest, on_delete=models.CASCADE)
    priority = models.IntegerField(choices=PRIORITY)

    class Meta:
        unique_together = ('student', 'interest')

class ThesisSkill(models.Model):
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, related_name='thesis_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    required_level = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('thesis', 'skill')


class ThesisInterest(models.Model):
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, related_name='thesis_interests')
    interest = models.ForeignKey(ResearchInterest, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('thesis', 'interest')