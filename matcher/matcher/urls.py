from django.contrib import admin
from django.urls import path, include
from core import views
from core.views import ThesisListView, ThesisDetailView, ApplicationListView, ApplicationDetailView, UserListView, \
    StudentSkillView, ThesisSkillView, StudentInterestView, ThesisInterestView, NotificationListView, \
    StudentThesisListView, MyApplicationsView, ApplyToThesisView, MyNotificationsView, MyThesisListCreateView, \
    MyThesisApplicationsView, UpdateApplicationStatusView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),

    path("api/theses/", ThesisListView.as_view(), name="api-thesis-list"),
    path("api/theses/<int:pk>/", ThesisDetailView.as_view(), name="api-thesis-detail"),
    path("api/applications/", ApplicationListView.as_view(), name="api-application-list"),
    path("api/applications/<int:pk>/", ApplicationDetailView.as_view(), name="api-application-detail"),
    path("api/users/", UserListView.as_view(), name="api-user-list"),
    path("api/student-skills/", StudentSkillView.as_view(), name="api-student-skills"),
    path("api/student-interests/", StudentInterestView.as_view(), name="api-student-interests"),
    path("api/thesis-skills/", ThesisSkillView.as_view(), name="api-thesis-skills"),
    path("api/thesis-interests/", ThesisInterestView.as_view(), name="api-thesis-interests"),
    path("api/notifications/", NotificationListView.as_view(), name="api-notification-list"),

    # student API
    path("api/student/theses/", StudentThesisListView.as_view(), name="api-student-thesis-list"),
    path("api/student/applications/", MyApplicationsView.as_view(), name="api-my-applications"),
    path("api/student/apply/", ApplyToThesisView.as_view(), name="api-apply-thesis"),
    path("api/student/notifications/", MyNotificationsView.as_view(), name="api-my-notifications"),

    # supervisor API
    path("api/supervisor/theses/", MyThesisListCreateView.as_view(), name="api-my-theses"),
    path("api/supervisor/applications/", MyThesisApplicationsView.as_view(), name="api-my-thesis-applications"),
    path("api/supervisor/applications/<int:pk>/", UpdateApplicationStatusView.as_view(),
         name="api-update-application-status"),

    path("", include("core.urls")),
]
