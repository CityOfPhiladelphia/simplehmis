from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import fields
from django.forms import widgets
from django.utils.translation import ugettext as _
from . import forms
from . import models


class AdminSite(admin.AdminSite):
    site_header = _('Philadelphia Simple HMIS')


class HouseholdMemberInline (admin.TabularInline):
    model = models.HouseholdMember
    formset = forms.HouseholdMemberFormset
    raw_id_fields = ['client']
    readonly_fields = ['link_to_assessments']
    verbose_name = _('Household member')
    verbose_name_plural = _('Household members')

    extra = 0
    min_num = 1

    def link_to_assessments(self, obj=None):
        if obj is None or obj.id is None:
            return '(Click "Save and continue editing" below to see the entry assessment information)'
        else:
            client_url = reverse('admin:simplehmis_householdmember_change', args=(obj.id,))
            return (
                '<a id="client_{}_assessments_link" href="{}" onclick="showAdminPopup(this, \'nosuchfield\');" target="_blank">'.format(obj.id, client_url) +
                'Edit client assessments</a>'
            )
    link_to_assessments.allow_tags = True
    link_to_assessments.short_description = _('Assessments')

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj=obj)
        user = models.HMISUser(request.user)
        if not user.can_enroll_household():
            fields.remove('present_at_enrollment')
        return fields


class IsEnrolledListFilter(admin.SimpleListFilter):
    title = _('enrollment status')
    parameter_name = 'enrolled'

    def lookups(self, request, model_admin):
        return (
            ('-1', _('pending')),
            ('0', _('enrolled')),
            ('1', _('exited')),
        )

    def queryset(self, request, queryset):
        return queryset.filter_by_enrollment(self.value())


class HouseholdAdmin (admin.ModelAdmin):
    inlines = [HouseholdMemberInline]
    raw_id_fields = ['project']

    actions_on_top = actions_on_bottom = False
    list_display = ['members_display', 'is_enrolled', 'project', 'date_of_entry']
    search_fields = ['project__name', 'members__first', 'members__middle', 'members__last']

    class Media:
        js = ("js/show-strrep.js", "js/hmis-forms.js")
        css = {"all": ("css/hmis-forms.css",)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        user = models.HMISUser(request.user)
        if not user.is_superuser and user.is_project_staff():
            qs = qs.filter(project__in=user.projects.all())

        return qs\
            .select_related('project')\
            .prefetch_related('members')\
            .prefetch_related('members__entry_assessment')\
            .prefetch_related('members__exit_assessment')\
            .prefetch_related('members__client')

    def get_list_filter(self, request):
        list_filter = [IsEnrolledListFilter]
        user = models.HMISUser(request.user)
        if user.is_superuser or not user.is_project_staff():
            list_filter.append('project')
        return list_filter

    def lookup_allowed(self, lookup, value):
        if lookup in ('project__id__exact',):
            return True
        return super().lookup_allowed(lookup, value)


class ClientAdmin (admin.ModelAdmin):
    actions_on_top = actions_on_bottom = False
    list_display = ['name_display', 'ssn_display', 'dob']
    search_fields = ['first', 'middle', 'last', 'ssn']
    formfield_overrides = {
        fields.TextField: {'widget': widgets.TextInput(attrs={'size': '40'})},
    }



HEALTH_INSURANCE_RADIO_FIELDS = (
    ('health_insurance_medicaid', admin.HORIZONTAL),
    ('health_insurance_medicare', admin.HORIZONTAL),
    ('health_insurance_chip', admin.HORIZONTAL),
    ('health_insurance_va', admin.HORIZONTAL),
    ('health_insurance_employer', admin.HORIZONTAL),
    ('health_insurance_cobra', admin.HORIZONTAL),
    ('health_insurance_private', admin.HORIZONTAL),
    ('health_insurance_state', admin.HORIZONTAL),
)


HEALTH_INSURANCE_FIELDSETS = (
    (None, {
        'fields': ('health_insurance',)
    }),
    ('If client has health insurance...', {
        'classes': ('collapse',),
        'fields': (
            'health_insurance_medicaid',
            'health_insurance_medicare', 'health_insurance_chip',
            'health_insurance_va', 'health_insurance_employer',
            'health_insurance_cobra', 'health_insurance_private',
            'health_insurance_state', 'health_insurance_none_reason'
        )
    }),
)


DISABLING_CONDITION_FIELDSETS = (
    (None, {
        'fields': ('physical_disability', 'physical_disability_impairing',
            'developmental_disability', 'developmental_disability_impairing',
            'chronic_health', 'chronic_health_impairing',
            'hiv_aids', 'hiv_aids_impairing',
            'mental_health', 'mental_health_impairing',
            'substance_abuse', 'substance_abuse_impairing')
    }),
)

HOUSING_STATUS_FIELDSETS = (
    (None, {
        'fields': ('housing_status', 'homeless_at_least_one_year',
            'homeless_in_three_years', 'homeless_months_in_three_years',
            'homeless_months_prior', 'status_documented', 'prior_residence',
            'prior_residence_other', 'length_at_prior_residence')
    }),
)

DOMESTIC_VIOLENCE_FIELDSETS = (
    (None, {
        'fields': ('domestic_violence', 'domestic_violence_occurred')
    }),
)

DESTINATION_FIELDSETS = (
    (None, {
        'fields': ('destination', 'destination_other')
    }),
)


class ClientEntryAssessmentInline (admin.StackedInline):
    model = models.ClientEntryAssessment
    extra = 1
    radio_fields = dict(HEALTH_INSURANCE_RADIO_FIELDS)
    formfield_overrides = {
        fields.TextField: {'widget': widgets.TextInput(attrs={'size': '100'})},
    }
    fieldsets = (
        (None, {'fields': ('project_entry_date',)}),
    ) + HEALTH_INSURANCE_FIELDSETS \
      + DISABLING_CONDITION_FIELDSETS \
      + HOUSING_STATUS_FIELDSETS \
      + DOMESTIC_VIOLENCE_FIELDSETS

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj=obj)

        user = models.HMISUser(request.user)
        if user.can_enroll_household():
            fields.remove('project_entry_date')

        return fields


class ClientExitAssessmentInline (admin.StackedInline):
    model = models.ClientExitAssessment
    extra = 0
    radio_fields = dict(HEALTH_INSURANCE_RADIO_FIELDS)
    formfield_overrides = {
        fields.TextField: {'widget': widgets.TextInput(attrs={'size': '100'})},
    }
    fieldsets = (
        (None, {'fields': ('project_exit_date',)}),
    ) + HEALTH_INSURANCE_FIELDSETS \
      + DISABLING_CONDITION_FIELDSETS \
      + DOMESTIC_VIOLENCE_FIELDSETS \
      + DESTINATION_FIELDSETS


class ClientAnnualAssessmentInline (admin.StackedInline):
    model = models.ClientAnnualAssessment
    extra = 0
    radio_fields = dict(HEALTH_INSURANCE_RADIO_FIELDS)
    formfield_overrides = {
        fields.TextField: {'widget': widgets.TextInput(attrs={'size': '100'})},
    }
    fieldsets = (
        (None, {'fields': ('assessment_date',)}),
    ) + HEALTH_INSURANCE_FIELDSETS \
      + DISABLING_CONDITION_FIELDSETS \
      + DOMESTIC_VIOLENCE_FIELDSETS


class HouseholdMemberAdmin (admin.ModelAdmin):
    raw_id_fields = ('client',)
    exclude = ('household', 'present_at_enrollment')
    readonly_fields = ('hoh_relationship',)
    inlines = (
        ClientEntryAssessmentInline,
        ClientAnnualAssessmentInline,
        ClientExitAssessmentInline
    )

    actions_on_top = actions_on_bottom = False
    list_display = ['__str__', 'is_enrolled', 'project', 'project_entry_date', 'project_exit_date']
    search_fields = ['client__first', 'client__middle', 'client__last', 'client__ssn']

    class Media:
        js = ("js/show-strrep.js", "js/hmis-forms.js")
        css = {"all": ("css/hmis-forms.css",)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        user = models.HMISUser(request.user)
        if not user.is_superuser and user.is_project_staff():
            qs = qs.filter(household__project__in=user.projects.all())

        return qs\
            .select_related('client')\
            .select_related('entry_assessment')\
            .select_related('exit_assessment')\
            .select_related('household')\
            .select_related('household__project')\

    def get_list_filter(self, request):
        list_filter = [IsEnrolledListFilter]
        user = models.HMISUser(request.user)
        if user.is_superuser or not user.is_project_staff():
            list_filter.append('household__project')
        return list_filter

    def lookup_allowed(self, lookup, value):
        if lookup in ('household__project__id__exact',):
            return True
        return super().lookup_allowed(lookup, value)


class ProjectAdmin (admin.ModelAdmin):
    search_fields = ['name']
    filter_horizontal = ['admins']
    formfield_overrides = {
        fields.TextField: {'widget': widgets.TextInput(attrs={'size': '100'})},
    }

    actions_on_top = actions_on_bottom = False

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm('simplehmis.add_project'):
            return []
        else:
            return ['name', 'admins']

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        user = models.HMISUser(request.user)
        if not user.is_superuser and user.is_project_staff():
            projects = user.projects.all()
            if projects is not None:
                qs = qs.filter(id__in=[p.id for p in projects])

        return qs


site = AdminSite()

from django.contrib.auth.admin import Group, GroupAdmin, User, UserAdmin
site.register(Group, GroupAdmin)
site.register(User, UserAdmin)

site.register(models.Client, ClientAdmin)
site.register(models.Project, ProjectAdmin)
site.register(models.Household, HouseholdAdmin)
site.register(models.HouseholdMember, HouseholdMemberAdmin)
