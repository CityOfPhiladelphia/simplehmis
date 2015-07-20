from django.contrib import admin
from django.core.urlresolvers import reverse
from django.forms import ValidationError
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

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.member_count() >= 1:
            return 0
        else:
            return 1

    def link_to_assessments(self, obj=None):
        if obj is None or obj.id is None:
            return '(Save the household in order to edit the entry assessment information)'
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

    list_display = ['project', 'hoh', 'dependents_display']
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

    def get_form(self, request, obj=None, **kwargs):
        user_projects = request.user.projects.all()
        form_class = super().get_form(request, obj=obj, **kwargs)

        if len(user_projects) == 1:
            class ModifiedModelForm (form_class):
                def __init__(self, *args, **kwargs):
                    kwargs.setdefault('initial', {})
                    kwargs['initial']['project'] = user_projects[0]
                    super().__init__(*args, **kwargs)
            form_class = ModifiedModelForm

        return form_class

    def get_fields(self, request, obj=None):
        user = models.HMISUser(request.user)
        fields = super().get_fields(request, obj=obj)
        if not user.can_refer_household():
            fields.remove('intake_action')
        if not user.can_enroll_household():
            fields.remove('enrolled_at')
        return fields

    def get_readonly_fields(self, request, obj=None):
        user = models.HMISUser(request.user)
        fields = []
        if not user.can_enroll_household():
            fields.append('enrolled_at')
        if not user.can_refer_household():
            fields.append('arrived_at')
        return fields


class ClientAdmin (admin.ModelAdmin):
    list_display = ['name_display', 'ssn_display', 'dob']
    search_fields = ['first', 'middle', 'last', 'ssn']


class ClientEntryAssessmentInline (admin.StackedInline):
    model = models.ClientEntryAssessment
    extra = 1


class ClientExitAssessmentInline (admin.StackedInline):
    model = models.ClientExitAssessment
    extra = 1


class ClientAnnualAssessmentInline (admin.StackedInline):
    model = models.ClientAnnualAssessment
    extra = 0


class HouseholdMemberAdmin (admin.ModelAdmin):
    raw_id_fields = ('client',)
    exclude = ('household',)

    def get_inline_instances(self, request, obj=None):
        user = models.HMISUser(request.user)
        if user.is_superuser or user.can_enroll_household():
            inlines = (
                ClientEntryAssessmentInline,
                ClientAnnualAssessmentInline,
                ClientExitAssessmentInline
            )
        else:
            inlines = ()
        return [inline(self.model, self.admin_site) for inline in inlines]


class ProjectAdmin (admin.ModelAdmin):
    search_fields = ['name']

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
