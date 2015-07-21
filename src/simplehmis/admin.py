from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import fields
from django.forms import ValidationError
from django.forms import widgets
from django.utils.translation import ugettext as _
from . import forms
from . import models


class AdminSite(admin.AdminSite):
    site_header = 'Philadenphia Simple HMIS'


class HouseholdMemberFormset (forms.RequiredInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        hoh_count = 0
        for form in self.forms:
            relationship = form.cleaned_data['hoh_relationship']
            if relationship == 1:
                hoh_count += 1
        if hoh_count != 1:
            raise ValidationError(_('There should be exactly one head of household.'))


class HouseholdMemberInline (admin.TabularInline):
    model = models.HouseholdMember
    formset = HouseholdMemberFormset
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
                '<a href="{}" target="_blank">'.format(client_url) +
                'Edit client assessments</a>'
            )
    link_to_assessments.allow_tags = True
    link_to_assessments.short_description = _('Assessments')


class HouseholdAdmin (admin.ModelAdmin):
    inlines = [HouseholdMemberInline]
    raw_id_fields = ['project']

    list_display = ['members_display', 'is_enrolled']
    search_fields = ['project__name', 'members__first', 'members__middle', 'members__last']

    class Media:
        js = ("js/show-strrep.js", "js/hmis-forms.js")
        css = {"all": ("css/hmis-forms.css",)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        user = models.HMISUser(request.user)
        if not user.is_superuser and user.is_project_staff():
            qs = qs.filter(project__in=user.projects.all())

        qs.prefetch_related('members')
        return qs


class ClientAdmin (admin.ModelAdmin):
    list_display = ['name_display', 'ssn_display', 'dob']
    search_fields = ['first', 'middle', 'last', 'ssn']


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
    fieldsets = (
        (None, {'fields': ('project_entry_date',)}),
    ) + HEALTH_INSURANCE_FIELDSETS \
      + DISABLING_CONDITION_FIELDSETS \
      + HOUSING_STATUS_FIELDSETS \
      + DOMESTIC_VIOLENCE_FIELDSETS


class ClientExitAssessmentInline (admin.StackedInline):
    model = models.ClientExitAssessment
    extra = 0
    radio_fields = dict(HEALTH_INSURANCE_RADIO_FIELDS)
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

    list_display = ['__str__', 'is_enrolled']

    class Media:
        js = ("js/show-strrep.js", "js/hmis-forms.js")
        css = {"all": ("css/hmis-forms.css",)}


class ProjectAdmin (admin.ModelAdmin):
    search_fields = ['name']
    filter_horizontal = ['admins']
    formfield_overrides = {
        fields.TextField: {'widget': widgets.TextInput(attrs={'size': '100'})},
    }

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm('simplehmis.add_project'):
            return []
        elif obj in request.user.projects.all():
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
