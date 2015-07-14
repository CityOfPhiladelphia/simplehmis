from django.contrib import admin
from django.utils.translation import ugettext as _
from . import models


class HOHEnrollmentInline (admin.StackedInline):
    model = models.ClientEnrollment
    fk_name = 'enrollment_as_hoh'
    exclude = ['hoh_relationship']
    raw_id_fields = ['client']
    verbose_name = _('Client Information')
    verbose_name_plural = _('Head of Household')

    def save_model(self, request, obj, form, change):
        obj.hoh_relationship = 1  # 1 -> Self (head of household)
        return super().save_model(request, obj, form, change)


class DependentEnrollmentInline (admin.StackedInline):
    model = models.ClientEnrollment
    fk_name = 'enrollment_as_dependant'
    extra = 0
    raw_id_fields = ['client']
    verbose_name = _('Dependent')
    verbose_name_plural = _('Dependents')


class EnrollmentAdmin (admin.ModelAdmin):
    inlines = [HOHEnrollmentInline, DependentEnrollmentInline]
    raw_id_fields = ['project']


class ClientAdmin (admin.ModelAdmin):
    list_display = ['name_display', 'ssn_display', 'dob']
    search_fields = ['first', 'middle', 'last', 'ssn']


class ProjectAdmin (admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Project)
admin.site.register(models.Enrollment, EnrollmentAdmin)
