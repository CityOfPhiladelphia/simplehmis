from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from simplehmis import models, admin

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


class AdminTests (TestCase):
    fixtures = ['staff-groups.yaml', 'hmis-test-data.yaml']

    def test_project_staff_only_see_members_in_their_programs(self):
        request = RequestFactory().get('/simplehmis/householdmembers')
        admin_view = admin.HouseholdMemberAdmin(models.HouseholdMember, admin.site)
        # Set the first project admin as the request user.
        project_admin = User.objects.get(username='project-admin1')
        request.user = project_admin
        # Make sure the project_admin only sees members in
        # their own their own projects.
        qs = admin_view.get_queryset(request)
        projects = project_admin.projects.all()
        assert all(member.household.project in projects for member in qs), \
            "Some projects in {} not in {}".format(
                [member.household.project for member in qs], projects)

    def test_project_staff_only_see_households_in_their_programs(self):
        request = RequestFactory().get('/simplehmis/households')
        admin_view = admin.HouseholdAdmin(models.Household, admin.site)
        # Set the first project admin as the request user.
        project_admin = User.objects.get(username='project-admin1')
        request.user = project_admin
        # Make sure the project_admin only sees households
        # in their own their own projects.
        qs = admin_view.get_queryset(request)
        projects = project_admin.projects.all()
        assert all(household.project in projects for household in qs), \
            "Some projects in {} not in {}".format(
                [household.project for household in qs], projects)


class EnrollmentFilterTests (TestCase):
    fixtures = ['staff-groups.yaml', 'hmis-test-data.yaml']

    def test_householdmember_pending_status(self):
        pending_members = models.HouseholdMember.objects.filter_by_enrollment('-1')
        assert len(pending_members) == 5
        assert set(member.client.first for member in pending_members) == set(['Ronny', 'Rashad', 'Orlando', 'Marisol', 'Kendrick'])

    def test_householdmember_enrolled_status(self):
        enrolled_members = models.HouseholdMember.objects.filter_by_enrollment('0')
        assert len(enrolled_members) == 2
        assert set(member.client.first for member in enrolled_members) == set(['Franklin', 'Magda'])

    def test_householdmember_exited_status(self):
        exited_members = models.HouseholdMember.objects.filter_by_enrollment('1')
        assert len(exited_members) == 3
        assert set(member.client.first for member in exited_members) == set(['Eunice', 'Dorris', 'Hung'])

