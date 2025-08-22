from rest_framework import permissions
from .models import Thesis, Application, StudentSkill, StudentInterest, ThesisSkill, ThesisInterest

def is_student(user):
    return user.is_authenticated and user.role == "student"

def is_supervisor(user):
    return user.is_authenticated and user.role == "supervisor"

def is_admin(user):
    return user.is_authenticated and user.is_staff

class IsSelfOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or is_admin(request.user)

class ThesisPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Thesis):
        user = request.user
        if is_admin(user):
            return True
        if is_student(user):
            return request.method in permissions.SAFE_METHODS and obj.status == "Open"
        if is_supervisor(user):
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.supervisor_id == user.id
        return False


class ApplicationPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Application):
        user = request.user
        if is_admin(user):
            return True
        if is_student(user):
            if obj.student_id != user.id:
                return False
            if request.method in permissions.SAFE_METHODS:
                return True
            return request.data.get("status") == "Withdrawn" or request.method == "DELETE"
        if is_supervisor(user):
            return obj.thesis.supervisor_id == user.id
        return False

class StudentDataPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if is_admin(user):
            return True
        if is_student(user):
            return obj.student_id == user.id
        if is_supervisor(user):
            if request.method in permissions.SAFE_METHODS:
                applied_students = Application.objects.filter(
                    thesis__supervisor=user
                ).values_list("student_id", flat=True)
                return obj.student_id in applied_students
            return False
        return False

class ThesisDataPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if is_admin(user):
            return True
        if is_student(user):
            return request.method in permissions.SAFE_METHODS
        if is_supervisor(user):
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.thesis.supervisor_id == user.id
        return False
