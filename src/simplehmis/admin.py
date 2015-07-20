from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import fields
from django.forms import ValidationError
from django.forms import widgets
from django.utils.translation import ugettext as _
from . import forms
from . import models


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


class ClientEntryAssessmentInline (admin.StackedInline):
    model = models.ClientEntryAssessment
    extra = 1


class ClientExitAssessmentInline (admin.StackedInline):
    model = models.ClientExitAssessment
    extra = 0


class ClientAnnualAssessmentInline (admin.StackedInline):
    model = models.ClientAnnualAssessment
    extra = 0


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


admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Household, HouseholdAdmin)
admin.site.register(models.HouseholdMember, HouseholdMemberAdmin)
