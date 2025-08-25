from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from .permissions import (
    IsSelfOrReadOnly,
    ThesisPermission,
    ApplicationPermission,
    StudentDataPermission,
    ThesisDataPermission,
)
from .models import User, Thesis, Application, StudentSkill, StudentInterest, ThesisSkill, ThesisInterest, Notification
from .serializers import (
    UserSerializer,
    ThesisSerializer,
    ApplicationSerializer,
    StudentSkillSerializer,
    StudentInterestSerializer,
    ThesisSkillSerializer,
    ThesisInterestSerializer,
    NotificationSerializer,
)

from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Thesis, Application
from .serializers import UserSerializer, ThesisSerializer, ApplicationSerializer

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm

from django.contrib.auth.models import Group
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsCoordinatorOrReadOnly(BasePermission):
    #Only supervisors can create/update/delete theses.
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user.is_authenticated and request.user.role == "supervisor"

class ApplicationPermission(BasePermission):
    #Students can create applications.
    #Students can update only their own applications (e.g., withdraw).
    #Coordinators can update applications for their theses (accept/reject).
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        #Students can only edit their own applications
        if request.user.role == "student":
            return obj.student == request.user

        #Coordinators can manage applications for theses they supervise
        if request.user.role == "supervisor":
            return obj.thesis.supervisor == request.user

        return False

#List all theses
class ThesisListView(generics.ListCreateAPIView):
    queryset = Thesis.objects.all()
    serializer_class = ThesisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["department", "status", "supervisor__id"]
    permission_classes = [IsAuthenticated, ThesisPermission]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == "student":
            return qs.filter(status="Open")
        if self.request.user.role == "supervisor":
            return qs.filter(supervisor=self.request.user)
        return qs

#Retrieve single thesis
class ThesisDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Thesis.objects.all()
    serializer_class = ThesisSerializer
    permission_classes = [IsAuthenticated, ThesisPermission]

class ApplicationListView(generics.ListCreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, ApplicationPermission]

class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, ApplicationPermission]

class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrReadOnly]

class StudentSkillView(generics.ListCreateAPIView):
    queryset = StudentSkill.objects.all()
    serializer_class = StudentSkillSerializer
    permission_classes = [IsAuthenticated, StudentDataPermission]


class StudentInterestView(generics.ListCreateAPIView):
    queryset = StudentInterest.objects.all()
    serializer_class = StudentInterestSerializer
    permission_classes = [IsAuthenticated, StudentDataPermission]


class ThesisSkillView(generics.ListCreateAPIView):
    queryset = ThesisSkill.objects.all()
    serializer_class = ThesisSkillSerializer
    permission_classes = [IsAuthenticated, ThesisDataPermission]


class ThesisInterestView(generics.ListCreateAPIView):
    queryset = ThesisInterest.objects.all()
    serializer_class = ThesisInterestSerializer
    permission_classes = [IsAuthenticated, ThesisDataPermission]

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = user.role

            if role == "student":
                group = Group.objects.get(name="Students")
            elif role == "supervisor":
                group = Group.objects.get(name="Coordinators")
            user.groups.add(group)

            login(request, user)
            return redirect("profile")
    else:
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form})

@login_required
def profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, "profile.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by("-created_at")