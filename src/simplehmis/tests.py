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


class EnrollmentFilterTests (TestCase):
    fixtures = ['staff-groups.yaml', 'hmis-test-data.yaml']

    def test_householdmember_pending_status(self):
        pending_members = models.HouseholdMember.objects.filter_by_enrollment('-1')
        assert len(pending_members) == 3
        assert set(member.client.first for member in pending_members) == set(['Marisol', 'Rashad', 'Orlando'])

    def test_householdmember_enrolled_status(self):
        enrolled_members = models.HouseholdMember.objects.filter_by_enrollment('0')
        assert len(enrolled_members) == 2
        assert set(member.client.first for member in enrolled_members) == set(['Franklin', 'Magda'])

    def test_householdmember_exited_status(self):
        exited_members = models.HouseholdMember.objects.filter_by_enrollment('1')
        assert len(exited_members) == 2
        assert set(member.client.first for member in exited_members) == set(['Eunice', 'Dorris'])
