from django.test import TestCase
from django.contrib.auth import get_user_model
from simplehmis import models

User = get_user_model()


class HMISUserTests (TestCase):
    fixtures = ['staff-groups.yaml', 'hmis-test-data.yaml']

    def test_group_names(self):
        intake_admin = models.HMISUser(User.objects.get(username='intake-admin'))
        self.assertEqual(list(intake_admin.group_names()), ['intake-staff'])

    def test_is_intake_staff(self):
        intake_admin = models.HMISUser(User.objects.get(username='intake-admin'))
        project_admin = models.HMISUser(User.objects.get(username='project-admin1'))
        assert intake_admin.is_intake_staff()
        assert not project_admin.is_intake_staff()

    def test_is_project_staff(self):
        intake_admin = models.HMISUser(User.objects.get(username='intake-admin'))
        project_admin = models.HMISUser(User.objects.get(username='project-admin1'))
        assert project_admin.is_project_staff()
        assert not intake_admin.is_project_staff()
