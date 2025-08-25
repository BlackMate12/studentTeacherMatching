"""
URL configuration for matcher project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from core.views import ThesisListView, ThesisDetailView, ApplicationListView, ApplicationDetailView, UserListView, \
    logout_view, StudentSkillView, ThesisSkillView, StudentInterestView, ThesisInterestView, NotificationListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/theses/", ThesisListView.as_view(), name="thesis-list"),
    path("api/theses/<int:pk>/", ThesisDetailView.as_view(), name="thesis-detail"),
    path("api/applications/", ApplicationListView.as_view(), name="application-list"),
    path("api/applications/<int:pk>/", ApplicationDetailView.as_view(), name="application-detail"),
    path("api/users/", UserListView.as_view(), name="user-list"),
    path("api/student-skills/", StudentSkillView.as_view(), name="student-skills"),
    path("api/student-interests/", StudentInterestView.as_view(), name="student-interests"),
    path("api/thesis-skills/", ThesisSkillView.as_view(), name="thesis-skills"),
    path("api/thesis-interests/", ThesisInterestView.as_view(), name="thesis-interests"),
    path("api/notifications/", NotificationListView.as_view(), name="notification-list"),
    path("", include("core.urls")),

]

