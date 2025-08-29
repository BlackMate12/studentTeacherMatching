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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, StudentInterestForm, StudentSkillForm, ThesisForm, ApplicationForm

from django.contrib.auth.models import Group
from rest_framework.permissions import BasePermission, SAFE_METHODS

from django.contrib import messages
from django.urls import reverse

from django.db.models import Count, Q, OuterRef, Subquery

#too much to keep track..........
class IsCoordinatorOrReadOnly(BasePermission):
    #Only supervisors can create/update/delete theses.
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
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
                group, _ = Group.objects.get_or_create(name="Students")
            elif role == "supervisor":
                group, _ = Group.objects.get_or_create(name="Coordinators")
            user.groups.add(group)

            login(request, user)
            return redirect("dashboard")
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

@login_required
def dashboard(request):
    role = request.user.role
    return render(request, "dashboard.html", {"role": role})

def logout_view(request):
    logout(request)
    return redirect("login")

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by("-created_at")

# Students: list only *open* theses
class StudentThesisListView(generics.ListAPIView):
    serializer_class = ThesisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Thesis.objects.filter(status=Thesis.Status.OPEN)

# Students: see their own applications
class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user)

# Students: create an application for a thesis
class ApplyToThesisView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

# Students: see their notifications
class MyNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by("-created_at")

# Supervisors: manage their own theses
class MyThesisListCreateView(generics.ListCreateAPIView):
    serializer_class = ThesisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Thesis.objects.filter(supervisor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(supervisor=self.request.user)


# Supervisors: see all applications for THEIR theses
class MyThesisApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(thesis__supervisor=self.request.user)


# Supervisors: update (accept/reject) applications
class UpdateApplicationStatusView(generics.RetrieveUpdateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Supervisors can only modify applications for their theses
        return Application.objects.filter(thesis__supervisor=self.request.user)

    def perform_update(self, serializer):
        application = serializer.save()
        # Create notification for student
        Notification.objects.create(
            recipient=application.student,
            message=f"Your application for '{application.thesis.title}' was {application.status}."
        )

class MySkillsView(generics.ListCreateAPIView):
    serializer_class = StudentSkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudentSkill.objects.filter(student=self.request.user)


class MyInterestsView(generics.ListCreateAPIView):
    serializer_class = StudentInterestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudentInterest.objects.filter(student=self.request.user)

# STUDENT & SUPERVISOR DASHBOARD
@login_required
def dashboard(request):
    role = request.user.role
    return render(request, "dashboard.html", {"role": role})

# THESIS LIST (human-readable)
@login_required
def theses_list(request):
    if request.user.role == "student":
        # Annotate supervisors with total accepted applications
        supervisors_with_counts = (
            Application.objects
            .filter(thesis__supervisor=OuterRef("supervisor"), status=Application.Status.ACCEPTED)
            .values("thesis__supervisor")
            .annotate(total=Count("id"))
            .values("total")
        )

        theses = (
            Thesis.objects.filter(status=Thesis.Status.OPEN)
            .annotate(supervisor_accepted_count=Subquery(supervisors_with_counts[:1]))
            .filter(Q(supervisor_accepted_count__lt=7) | Q(supervisor_accepted_count__isnull=True))
        )

    elif request.user.role == "supervisor":
        theses = Thesis.objects.all()

    return render(request, "theses.html", {"theses": theses})


# THESIS DETAIL + APPLY (student can apply from here)
@login_required
def thesis_detail(request, pk):
    thesis = get_object_or_404(Thesis, pk=pk)
    can_apply = request.user.role == "student" and thesis.status == Thesis.Status.OPEN
    # check if student already applied
    already_applied = Application.objects.filter(student=request.user, thesis=thesis).exists() if request.user.role == "student" else False

    if request.method == "POST" and can_apply and not already_applied:
        form = ApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.student = request.user
            app.thesis = thesis
            app.status = Application.Status.PENDING
            app.save()
            # notify supervisor
            Notification.objects.create(recipient=thesis.supervisor, message=f"{request.user.username} applied to your thesis '{thesis.title}'.")
            messages.success(request, "Application submitted.")
            return redirect("thesis-detail", pk=thesis.pk)
    else:
        form = ApplicationForm()

    return render(request, "thesis_detail.html", {
        "thesis": thesis,
        "form": form,
        "can_apply": can_apply,
        "already_applied": already_applied,
    })

# STUDENT: My Applications
@login_required
def my_applications(request):
    if request.user.role != "student":
        return redirect("dashboard")
    apps = Application.objects.filter(student=request.user).order_by("-application_date")
    return render(request, "my_applications.html", {"applications": apps})

# SUPERVISOR: Applications to my theses
@login_required
def supervisor_applications(request):
    if request.user.role != "supervisor":
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    apps = Application.objects.filter(thesis__supervisor=request.user).order_by("-application_date")
    return render(request, "supervisor_applications.html", {"applications": apps})

# SUPERVISOR: accept/reject via POST
@login_required
def update_application_status(request, pk):
    app = get_object_or_404(Application, pk=pk, thesis__supervisor=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accept":
            # count accepted applications for this supervisor across ALL their theses
            accepted_count = Application.objects.filter(
                thesis__supervisor=request.user,
                status=Application.Status.ACCEPTED,
            ).count()

            if accepted_count >= 7:
                messages.error(request, "You cannot accept more than 7 students across all your theses.")
            elif not app.thesis.has_capacity:
                messages.error(request, "Thesis has no capacity.")
            else:
                app.status = Application.Status.ACCEPTED
                app.save()
                Notification.objects.create(
                    recipient=app.student,
                    message=f"Your application for '{app.thesis.title}' was accepted."
                )
                messages.success(request, "Application accepted.")

        elif action == "reject":
            app.status = Application.Status.REJECTED
            app.save()
            Notification.objects.create(
                recipient=app.student,
                message=f"Your application for '{app.thesis.title}' was rejected."
            )
            messages.success(request, "Application rejected.")

        return redirect("supervisor-applications")

    return render(request, "supervisor_applications.html", {"application": app})


# SUPERVISOR: My Theses (list + create)
@login_required
def my_theses(request):
    if request.user.role != "supervisor":
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    theses = Thesis.objects.filter(supervisor=request.user)
    return render(request, "my_theses.html", {"theses": theses})

@login_required
def create_thesis(request):
    if request.user.role != "supervisor":
        messages.error(request, "Access denied.")
        return redirect("dashboard")
    if request.method == "POST":
        form = ThesisForm(request.POST)
        if form.is_valid():
            thesis = form.save(commit=False)
            thesis.supervisor = request.user
            thesis.save()
            form.save_m2m()
            messages.success(request, "Thesis created.")
            return redirect("my-theses")
    else:
        form = ThesisForm()
    return render(request, "create_thesis.html", {"form": form})

@login_required
def edit_thesis(request, pk):
    thesis = get_object_or_404(Thesis, pk=pk, supervisor=request.user)
    if request.method == "POST":
        form = ThesisForm(request.POST, instance=thesis)
        if form.is_valid():
            form.save()
            messages.success(request, "Thesis updated.")
            return redirect("my-theses")
    else:
        form = ThesisForm(instance=thesis)
    return render(request, "edit_thesis.html", {"form": form, "thesis": thesis})

# STUDENT: My skills & interests (list/add/delete)
@login_required
def my_skills(request):
    if request.method == "POST":
        form = StudentSkillForm(request.POST)
        if form.is_valid():
            skill_obj = form.save(commit=False)
            skill_obj.student = request.user
            try:
                skill_obj.save()
                messages.success(request, "Skill added.")
            except Exception:
                messages.error(request, "Skill already added.")
            return redirect("my-skills")
    else:
        form = StudentSkillForm()
    skills = StudentSkill.objects.filter(student=request.user)
    return render(request, "skills.html", {"skills": skills, "form": form})

@login_required
def delete_skill(request, pk):
    sk = get_object_or_404(StudentSkill, pk=pk, student=request.user)
    sk.delete()
    messages.success(request, "Skill removed.")
    return redirect("my-skills")

@login_required
def my_interests(request):
    if request.method == "POST":
        form = StudentInterestForm(request.POST)
        if form.is_valid():
            int_obj = form.save(commit=False)
            int_obj.student = request.user
            try:
                int_obj.save()
                messages.success(request, "Interest added.")
            except Exception:
                messages.error(request, "Interest already added.")
            return redirect("my-interests")
    else:
        form = StudentInterestForm()
    interests = StudentInterest.objects.filter(student=request.user)
    return render(request, "interests.html", {"interests": interests, "form": form})

@login_required
def delete_interest(request, pk):
    it = get_object_or_404(StudentInterest, pk=pk, student=request.user)
    it.delete()
    messages.success(request, "Interest removed.")
    return redirect("my-interests")

# Notifications (for both roles)
@login_required
def web_notifications(request):
    notes = Notification.objects.filter(recipient=request.user).order_by("-created_at")
    return render(request, "notifications.html", {"notifications": notes})

@login_required
def apply_to_thesis(request, pk):
    thesis = get_object_or_404(Thesis, pk=pk)

    if request.user.role != "student":
        messages.error(request, "Only students can apply to theses.")
        return redirect("theses")

    if Application.objects.filter(student=request.user, status="pending").exists():
        messages.warning(request, "You already have a pending application. Withdraw it before applying again.")
        return redirect("theses")

    if request.method == "POST":
        # prevent duplicate application
        if Application.objects.filter(student=request.user, thesis=thesis).exists():
            messages.warning(request, "You already applied for this thesis.")
        else:
            motivation_letter = request.POST.get("motivation", "").strip()
            Application.objects.create(
                student=request.user,
                thesis=thesis,
                motivation_letter=motivation_letter,
                status="pending"
            )
            messages.success(request, "Application submitted successfully.")

    return redirect("theses")


@login_required
def delete_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.delete()
    messages.success(request, "Notification deleted.")
    return redirect("web-notifications")

from django.contrib.auth.forms import UserChangeForm

@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, "profile_edit.html", {"form": form})


@login_required
def withdraw_application(request, pk):
    app = get_object_or_404(Application, pk=pk, student=request.user, status="pending")
    if request.method == "POST":
        app.status = "withdrawn"
        app.save()
        messages.info(request, "Application withdrawn.")
    return redirect("my-applications")

@login_required
def matched_theses(request):
    if request.user.role != "student":
        messages.error(request, "Only students can view matched theses.")
        return redirect("dashboard")

    # Collect the student's skills and interests (just the IDs)
    student_skill_ids = StudentSkill.objects.filter(student=request.user).values_list("skill_id", flat=True)
    student_interest_ids = StudentInterest.objects.filter(student=request.user).values_list("interest_id", flat=True)

    # Match theses by overlapping required_skills or interests
    theses = (
        Thesis.objects.filter(status=Thesis.Status.OPEN)
        .annotate(
            shared_skills=Count(
                "required_skills",
                filter=Q(required_skills__in=student_skill_ids),
                distinct=True,
            ),
            shared_interests=Count(
                "interests",
                filter=Q(interests__in=student_interest_ids),
                distinct=True,
            ),
        )
        .filter(Q(shared_skills__gte=2) | Q(shared_interests__gte=2))
    )

    return render(request, "matched_theses.html", {"theses": theses})

