from django.test import TestCase, RequestFactory
from django.conf import settings
from django.contrib.auth import get_user_model
from simplehmis import models, admin

User = get_user_model()


class HMISUserTests (TestCase):
    fixtures = ['staff-groups', 'hmis-test-data']

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
    fixtures = ['staff-groups', 'hmis-test-data']

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

    def test_project_staff_only_see_their_programs(self):
        request = RequestFactory().get('/simplehmis/projects')
        admin_view = admin.ProjectAdmin(models.Project, admin.site)
        # Set the first project admin as the request user.
        project_admin = User.objects.get(username='project-admin1')
        request.user = project_admin
        # Make sure the project_admin only sees their own
        # projects.
        qs = admin_view.get_queryset(request)
        projects = project_admin.projects.all()
        assert all(project in projects for project in qs), \
            "Some projects in {} not in {}".format(qs, projects)

    def test_intake_staff_see_all_households(self):
        request = RequestFactory().get('/simplehmis/households')
        admin_view = admin.HouseholdAdmin(models.Household, admin.site)
        # Set the intake admin as the request user.
        intake_admin = User.objects.get(username='intake-admin')
        request.user = intake_admin
        # Make sure the intake_admin only sees households
        # in their own their own projects.
        qs_households = set(admin_view.get_queryset(request))
        all_households = set(models.Household.objects.all())
        assert qs_households == all_households, \
            "Some households are missing from the queryset: {}".format(
                all_households - qs_households)

    def test_dual_staff_see_all_households(self):
        request = RequestFactory().get('/simplehmis/households')
        admin_view = admin.HouseholdAdmin(models.Household, admin.site)
        # Set the dual admin as the request user.
        dual_admin = User.objects.get(username='dual-admin')
        request.user = dual_admin
        # Make sure the dual_admin sees all households.
        qs_households = set(admin_view.get_queryset(request))
        all_households = set(models.Household.objects.all())
        assert qs_households == all_households, \
            "Some households are missing from the queryset: {}".format(
                all_households - qs_households)

    def test_dual_staff_see_all_projects(self):
        request = RequestFactory().get('/simplehmis/projects')
        admin_view = admin.ProjectAdmin(models.Project, admin.site)
        # Set the dual admin as the request user.
        dual_admin = User.objects.get(username='dual-admin')
        request.user = dual_admin
        # Make sure the dual_admin sees all projects.
        qs_projects = set(admin_view.get_queryset(request))
        all_projects = set(models.Project.objects.all())
        assert qs_projects == all_projects, \
            "Some households are missing from the queryset: {}".format(
                all_projects - qs_projects)

    def test_superusers_can_dump_all_data(self):
        request = RequestFactory().get('/simplehmis/download_data')
        # Set the superuser as the request user.
        superuser = User.objects.get(username='admin')
        request.user = superuser
        # Make sure the superuser gets a zipfile.
        response = admin.dump_hud_data(request)
        assert response.status_code == 200

    def test_dual_staff_cannot_dump_all_data(self):
        request = RequestFactory().get('/simplehmis/download_data')
        # Set the dual_admin as the request user.
        dual_admin = User.objects.get(username='dual-admin')
        request.user = dual_admin
        # Make sure the dual_admin cannot get the download.
        response = admin.dump_hud_data(request)
        assert response.status_code == 302
        assert response.url.startswith(settings.LOGIN_URL)


class EnrollmentFilterTests (TestCase):
    fixtures = ['staff-groups', 'hmis-test-data']

    def test_householdmember_pending_status(self):
        pending_members = models.HouseholdMember.objects.filter_by_enrollment('-1')
        assert len(pending_members) == 6
        assert set(member.client.first for member in pending_members) == set(['Ronny', 'Rashad', 'Orlando', 'Marisol', 'Kendrick', 'Dannette'])

    def test_householdmember_enrolled_status(self):
        enrolled_members = models.HouseholdMember.objects.filter_by_enrollment('0')
        assert len(enrolled_members) == 5
        assert set(member.client.first for member in enrolled_members) == set(['Franklin', 'Magda', 'Nannie', 'Michal', 'Dorris'])

    def test_householdmember_exited_status(self):
        exited_members = models.HouseholdMember.objects.filter_by_enrollment('1')
        assert len(exited_members) == 3
        assert set(member.client.first for member in exited_members) == set(['Eunice', 'Hung', 'Sharika'])

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
        # This household has three members, one of whom is
        # marked as absent at enrollemnt. The other two do
        # have entry assessment dates and no exit dates.
        household = models.Household.objects.get(id=1)

        assert household.is_enrolled() is True
        assert household in models.Household.objects.filter_by_enrollment(0)
        assert household not in models.Household.objects.filter_by_enrollment(-1)
        assert household not in models.Household.objects.filter_by_enrollment(1)

        # This household has three members, one of whom is
        # marked as absent at enrollemnt. One of the others
        # has an entry and exit assessment, and the other
        # only has an entry assessment date.
        household = models.Household.objects.get(id=10)

        assert household.is_enrolled() is True
        assert household in models.Household.objects.filter_by_enrollment(0)
        assert household not in models.Household.objects.filter_by_enrollment(-1)
        assert household not in models.Household.objects.filter_by_enrollment(1)

    def test_household_exited_status(self):
        # This household has two members, one of whom is
        # marked as absent at enrollemnt. The other has an
        # exit assessment date.
        household = models.Household.objects.get(id=8)

        assert household.is_enrolled() is False
        assert household in models.Household.objects.filter_by_enrollment(1)
        assert household not in models.Household.objects.filter_by_enrollment(-1)
        assert household not in models.Household.objects.filter_by_enrollment(0)
