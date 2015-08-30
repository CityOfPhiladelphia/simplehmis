from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import fields
from django.forms import widgets
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from reversion import VersionAdmin
from . import forms
from . import models
from . import sites


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
            return render_to_string(
                'admin/_assessments_display.html',
                {'member': obj, 'url': client_url})
    link_to_assessments.allow_tags = True
    link_to_assessments.short_description = _('Assessments')

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj=obj)
        user = models.HMISUser(request.user)
        if not user.can_enroll_household():
            fields.remove('present_at_enrollment')
            fields.remove('entry_date')
            fields.remove('exit_date')
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


class HouseholdAdmin (VersionAdmin):
    inlines = [HouseholdMemberInline]
    raw_id_fields = ['project']

    actions_on_top = actions_on_bottom = False
    list_display = ['members_display', 'is_enrolled', 'project', 'date_of_intake', 'date_of_entry']
    search_fields = ['project__name', 'members__client__first', 'members__client__middle', 'members__client__last', 'members__client__ssn']

    class Media:
        js = ("js/show-strrep.js", "js/hmis-forms.js")
        css = {"all": ("css/hmis-forms.css",)}

    def date_of_intake(self, obj):
        return obj.created_at.date()
    date_of_intake.short_description = _('Date of referral')
    date_of_intake.admin_order_field = 'created_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        user = models.HMISUser(request.user)
        if not user.can_refer_household():
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
        if user.can_refer_household():
            list_filter.append('project')
        return list_filter

    def lookup_allowed(self, lookup, value):
        if lookup in ('project__id__exact',
                      'project__isnull',):
            return True
        return super().lookup_allowed(lookup, value)


class ClientAdmin (VersionAdmin):
    actions_on_top = actions_on_bottom = False
    list_display = ['name_display', 'ssn_display', 'dob']
    search_fields = ['first', 'middle', 'last', 'ssn']
    formfield_overrides = {
        fields.TextField: {'widget': widgets.TextInput(attrs={'size': '40'})},
    }
    fieldsets = (
        (None, {
            'fields': ('first', 'middle', 'last', 'suffix', 'dob', 'ssn',)
        }),
        (None, {
            'classes': ('fieldset-gender',),
            'fields': ('gender',)
        }),
        (None, {
            'classes': ('indent',),
            'fields': ('other_gender',)
        }),
        (None, {
            'fields': ('ethnicity', 'race', 'veteran_status',)
        })
    )

    class Media:
        js = ("js/show-strrep.js", "js/hmis-forms.js")
        css = {"all": ("css/hmis-forms.css",)}



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
        'classes': ('has-yes-dependency',),
        'fields': ('health_insurance',)
    }),
    (_('If client has health insurance, indicate all sources that apply:'), {
        'classes': ('health_insurance_sources', 'indent',),
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
        'classes': ('has-yes-dependency',),
        'fields': ('physical_disability',)
    }),
    (None, {
        'classes': ('indent',),
        'fields': ('physical_disability_impairing',)
    }),
    (None, {
        'classes': ('has-yes-dependency',),
        'fields': ('developmental_disability',)
    }),
    (None, {
        'classes': ('indent',),
        'fields': ('developmental_disability_impairing',)
    }),
    (None, {
        'classes': ('has-yes-dependency',),
        'fields': ('chronic_health',)
    }),
    (None, {
        'classes': ('indent',),
        'fields': ('chronic_health_impairing',)
    }),
    (None, {
        'classes': ('has-yes-dependency',),
        'fields': ('hiv_aids',)
    }),
    (None, {
        'classes': ('indent',),
        'fields': ('hiv_aids_impairing',)
    }),
    (None, {
        'classes': ('has-yes-dependency',),
        'fields': ('mental_health',)
    }),
    (None, {
        'classes': ('indent',),
        'fields': ('mental_health_impairing',)
    }),
    (None, {
        'classes': ('fieldset-substance_abuse', 'has-dependency',),
        'fields': ('substance_abuse',)
    }),
    (None, {
        'classes': ('indent',),
        'fields': ('substance_abuse_impairing',)
    }),
)

HOUSING_STATUS_FIELDSETS = (
    (None, {
        'fields': ('housing_status', 'homeless_at_least_one_year',)
    }),
    (None, {
        'classes': ('fieldset-homeless_in_three_years', 'has-dependency',),
        'fields': ('homeless_in_three_years',)
    }),
    (None, {
        'classes': ('indent',),
        'fields': ('homeless_months_in_three_years',)
    }),
    (None, {
        'fields': ('homeless_months_prior', 'status_documented',)
    }),
    (None, {
        'classes': ('fieldset-prior_residence', 'has-dependency',),
        'fields': ('prior_residence',)
    }),
    (None, {
        'classes': ('indent',),
        'fields': ('prior_residence_other',)
    }),
    (None, {
        'fields': ('length_at_prior_residence',)
    }),
)

INCOME_FIELDSETS = (
    (None, {
        'classes': ('has-yes-dependency',),
        'fields': ('income_status',)
    }),
    (None, {
        'classes': ('indent',),
        'fields': ('income_notes',)
    }),
)

DOMESTIC_VIOLENCE_FIELDSETS = (
    (None, {
        'classes': ('has-yes-dependency',),
        'fields': ('domestic_violence',)
    }),
    (None, {
        'classes': ('indent',),
        'fields': ('domestic_violence_occurred',)
    }),
)

DESTINATION_FIELDSETS = (
    (None, {
        'classes': ('fieldset-destination', 'has-dependency',),
        'fields': ('destination',)
    }),
    (None, {
        'classes': ('indent',),
        'fields': ('destination_other',)
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
      + DOMESTIC_VIOLENCE_FIELDSETS \
      + INCOME_FIELDSETS

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
      + INCOME_FIELDSETS \
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
      + DOMESTIC_VIOLENCE_FIELDSETS \
      + INCOME_FIELDSETS


class HouseholdMemberAdmin (VersionAdmin):
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
        if not user.can_refer_household():
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
        if user.can_refer_household():
            list_filter.append('household__project')
        return list_filter

    def lookup_allowed(self, lookup, value):
        if lookup in ('household__project__id__exact',
                      'household__project__isnull',):
            return True
        return super().lookup_allowed(lookup, value)


class ProjectAdmin (VersionAdmin):
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


from django.contrib.auth.admin import Group, GroupAdmin, User, UserAdmin


class HMISUserAdmin (UserAdmin):
    actions = ['send_onboarding_messages']
    add_form = forms.PasswordlessUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',),
        }),
    )

    def send_onboarding_messages(self, request, queryset):
        for user in queryset:
            user = models.HMISUser(user)
            user.send_onboarding_email(secure=(request.scheme == 'https'), host=request.get_host())

            count = len(queryset)
        self.message_user(request, 'Successfully sent {} onbaording message{}.'.format(count, '' if count == 1 else 's'))
    send_onboarding_messages.short_description = "Send onboarding emails to the selected users"


site = sites.HMISAdminSite()

site.register(Group, GroupAdmin)
site.register(User, HMISUserAdmin)

site.register(models.Client, ClientAdmin)
site.register(models.Project, ProjectAdmin)
site.register(models.Household, HouseholdAdmin)
site.register(models.HouseholdMember, HouseholdMemberAdmin)
