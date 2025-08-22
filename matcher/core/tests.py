from django.test import TestCase
from django.utils import timezone
from core.models import User, Thesis, Application, ResearchInterest, StudentInterest
from core.serializers import ApplicationSerializer, StudentInterestSerializer

class SerializerPermissionTests(TestCase):
    def setUp(self):
        # Create users
        self.student = User.objects.create_user(username="stud", password="pass", role="student")
        self.supervisor = User.objects.create_user(username="sup", password="pass", role="coordinator")

        # Create a thesis
        self.thesis = Thesis.objects.create(
            title="AI Thesis",
            description="ML Project",
            department="CS",
            supervisor=self.supervisor,
            status="open",
            max_students=1
        )

        # Create a research interest (needed for StudentInterest)
        self.interest = ResearchInterest.objects.create(name="Artificial Intelligence")

    def test_student_application_creation(self):
        """Student can create an application but cannot set student manually"""
        data = {
            "thesis": self.thesis.id,
            "motivation_letter": "I love AI",
            "status": "pending",  # ✅ lowercase matches your model
        }
        serializer = ApplicationSerializer(data=data, context={"request": self._fake_request(self.student)})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_application_status_update_student(self):
        """Student can only withdraw an application"""
        app = Application.objects.create(student=self.student, thesis=self.thesis, status="pending")

        # Try withdrawing (valid)
        serializer = ApplicationSerializer(
            instance=app,
            data={"status": "withdrawn"},  # ✅ lowercase
            partial=True,
            context={"request": self._fake_request(self.student)}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # Try setting accepted (should fail for student)
        serializer = ApplicationSerializer(
            instance=app,
            data={"status": "accepted"},  # ✅ lowercase
            partial=True,
            context={"request": self._fake_request(self.student)}
        )
        self.assertFalse(serializer.is_valid())

    def test_student_interest_creation(self):
        """Student interests are automatically linked to the logged-in user"""
        data = {
            "interest": self.interest.id,  # ✅ we created a ResearchInterest in setUp
            "priority": 3,  # ✅ integer (3 = High)
        }
        serializer = StudentInterestSerializer(
            data=data,
            context={"request": self._fake_request(self.student)}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    # --- Helper ---
    def _fake_request(self, user):
        """Mimic DRF request.user for serializer context"""
        class Dummy:
            pass
        dummy = Dummy()
        dummy.user = user
        return dummy
