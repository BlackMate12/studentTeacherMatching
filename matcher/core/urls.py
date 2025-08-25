from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import NotificationListView

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
]
