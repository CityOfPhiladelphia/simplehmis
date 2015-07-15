from django.contrib import admin
from django.utils.translation import ugettext as _
from . import models


class ClientEnrollmentInline (admin.StackedInline):
    model = models.ClientEnrollment
    raw_id_fields = ['client']
    verbose_name = _('Household member')
    verbose_name_plural = _('Household members')

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.hoh:
            return 0
        else:
            return 1


class EnrollmentAdmin (admin.ModelAdmin):
    inlines = [ClientEnrollmentInline]
    raw_id_fields = ['project']

    list_display = ['project', 'hoh', 'dependents_display']
    search_fields = ['project__name', 'members__first', 'members__middle', 'members__last']

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


class ProjectAdmin (admin.ModelAdmin):
    search_fields = ['name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        user = models.HMISUser(request.user)
        if not user.is_superuser and user.is_project_staff():
            qs = qs.filter(id__in=[p.id for p in user.projects.all()])

        return qs


admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Project)
admin.site.register(models.Enrollment, EnrollmentAdmin)
