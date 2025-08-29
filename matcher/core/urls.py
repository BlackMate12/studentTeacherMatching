from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import NotificationListView

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit-profile"),

    # dashboard + web UI
    path("dashboard/", views.dashboard, name="dashboard"),

    # theses
    path("theses/", views.theses_list, name="theses"),
    path("theses/<int:pk>/", views.thesis_detail, name="thesis-detail"),
    path("theses/<int:pk>/apply/", views.apply_to_thesis, name="apply-to-thesis"),


    # student actions
    path("student/applications/", views.my_applications, name="my-applications"),
    path("student/applications/<int:pk>/withdraw/", views.withdraw_application, name="withdraw-application"),

    path("student/skills/", views.my_skills, name="my-skills"),
    path("student/skills/<int:pk>/delete/", views.delete_skill, name="delete-skill"),
    path("student/interests/", views.my_interests, name="my-interests"),
    path("student/interests/<int:pk>/delete/", views.delete_interest, name="delete-interest"),
    path("student/theses/<int:pk>/apply/", views.apply_to_thesis, name="apply-to-thesis"),

    # supervisor actions
    path("supervisor/theses/", views.my_theses, name="my-theses"),
    path("supervisor/theses/create/", views.create_thesis, name="create-thesis"),
    path("supervisor/theses/<int:pk>/edit/", views.edit_thesis, name="edit-thesis"),
    path("supervisor/applications/", views.supervisor_applications, name="supervisor-applications"),
    path("supervisor/applications/<int:pk>/update/", views.update_application_status, name="update-application-status"),

    # notifications
    path("notifications/", views.web_notifications, name="web-notifications"),
    path("notifications/<int:pk>/delete/", views.delete_notification, name="delete-notification"),

]
