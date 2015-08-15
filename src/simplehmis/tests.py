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
        assert len(pending_members) == 6
        assert set(member.client.first for member in pending_members) == set(['Ronny', 'Rashad', 'Orlando', 'Marisol', 'Kendrick', 'Dannette'])

    def test_householdmember_enrolled_status(self):
        enrolled_members = models.HouseholdMember.objects.filter_by_enrollment('0')
        assert len(enrolled_members) == 4
        assert set(member.client.first for member in enrolled_members) == set(['Franklin', 'Magda', 'Nannie', 'Michal'])

    def test_householdmember_exited_status(self):
        exited_members = models.HouseholdMember.objects.filter_by_enrollment('1')
        assert len(exited_members) == 4
        assert set(member.client.first for member in exited_members) == set(['Eunice', 'Dorris', 'Hung', 'Sharika'])

    def test_household_pending_status(self):
        # This household has three members, one of whom is
        # marked as absent at enrollemnt. The other two do
        # not have entry assessment dates.
        household = models.Household.objects.get(id=7)

        assert household.is_enrolled() is None
        assert household in models.Household.objects.filter_by_enrollment(-1)
        assert household not in models.Household.objects.filter_by_enrollment(0)
        assert household not in models.Household.objects.filter_by_enrollment(1)

        # This household has three members, one of whom is
        # marked as absent at enrollemnt. One of the other
        # two has an entry assessment date, the other does
        # not..
        household = models.Household.objects.get(id=9)

        assert household.is_enrolled() is None
        assert household in models.Household.objects.filter_by_enrollment(-1)
        assert household not in models.Household.objects.filter_by_enrollment(0)
        assert household not in models.Household.objects.filter_by_enrollment(1)

    def test_household_enrolled_status(self):
        household = models.Household.objects.get(id=1)
        # This household has three members, one of whom is
        # marked as absent at enrollemnt. The other two do
        # have entry assessment dates.

        assert household.is_enrolled() is True
        assert household in models.Household.objects.filter_by_enrollment(0)
        assert household not in models.Household.objects.filter_by_enrollment(-1)
        assert household not in models.Household.objects.filter_by_enrollment(1)

        household = models.Household.objects.get(id=10)
        # This household has three members, one of whom is
        # marked as absent at enrollemnt. One of the others
        # has an entry and exit assessment, and the other
        # only has an entry assessment date.

        assert household.is_enrolled() is True
        assert household in models.Household.objects.filter_by_enrollment(0)
        assert household not in models.Household.objects.filter_by_enrollment(-1)
        assert household not in models.Household.objects.filter_by_enrollment(1)

    def test_household_exited_status(self):
        household = models.Household.objects.get(id=8)
        # This household has two members, one of whom is
        # marked as absent at enrollemnt. The other has an
        # exit assessment date.

        assert household.is_enrolled() is False
        assert household in models.Household.objects.filter_by_enrollment(1)
        assert household not in models.Household.objects.filter_by_enrollment(-1)
        assert household not in models.Household.objects.filter_by_enrollment(0)
