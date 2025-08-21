from django.contrib import admin
from .models import User, Thesis, Application, Skill, ResearchInterest, StudentInterest, ThesisSkill, ThesisInterest, StudentSkill

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "role", "department")

@admin.register(Thesis)
class ThesisAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "supervisor", "status", "max_students")
    list_filter = ("status", "department")

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "thesis", "status", "application_date")
    list_filter = ("status",)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)

@admin.register(ResearchInterest)
class ResearchInterestAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)

@admin.register(StudentInterest)
class StudentInterestAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "interest", "priority")

@admin.register(ThesisSkill)
class ThesisSkillAdmin(admin.ModelAdmin):
    list_display = ("id", "thesis", "skill")

@admin.register(ThesisInterest)
class ThesisInterestAdmin(admin.ModelAdmin):
    list_display = ("id", "thesis", "interest")

@admin.register(StudentSkill)
class StudentSkillAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "skill")
