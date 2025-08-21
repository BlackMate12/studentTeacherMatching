from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Thesis, Application
from .serializers import UserSerializer, ThesisSerializer, ApplicationSerializer

# List all theses
class ThesisListView(generics.ListCreateAPIView):
    queryset = Thesis.objects.all()
    serializer_class = ThesisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["department", "status", "supervisor__id"]  # e.g. filter by dept or status

    def get_queryset(self):
        qs = super().get_queryset()
        # If user is student → only open theses
        if self.request.user.role == "student":
            return qs.filter(status="Open")
        # If coordinator → see only their theses
        if self.request.user.role == "coordinator":
            return qs.filter(supervisor=self.request.user)
        return qs

# Retrieve single thesis
class ThesisDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Thesis.objects.all()
    serializer_class = ThesisSerializer

# List all applications (student -> thesis)
class ApplicationListView(generics.ListCreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

# Single application
class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

# Simple student/professor listing
class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
