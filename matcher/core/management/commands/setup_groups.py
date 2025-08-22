from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from core.models import User

class Command(BaseCommand):
    help = "Setup default groups and permissions"

    def handle(self, *args, **kwargs):
        students_group, _ = Group.objects.get_or_create(name="Students")
        student_perms = Permission.objects.filter(
            codename__in=[
                "add_application",
                "view_thesis",
                "view_application",
            ]
        )
        students_group.permissions.set(student_perms)

        coordinators_group, _ = Group.objects.get_or_create(name="Coordinators")
        coordinator_perms = Permission.objects.filter(
            codename__in=[
                "add_thesis", "change_thesis", "delete_thesis",
                "view_thesis",
                "view_application", "change_application",
            ]
        )
        coordinators_group.permissions.set(coordinator_perms)

        self.stdout.write(self.style.SUCCESS("Groups and permissions created."))