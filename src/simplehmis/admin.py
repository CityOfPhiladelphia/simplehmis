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


class ClientAdmin (admin.ModelAdmin):
    list_display = ['name_display', 'ssn_display', 'dob']
    search_fields = ['first', 'middle', 'last', 'ssn']


class ProjectAdmin (admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Project)
admin.site.register(models.Enrollment, EnrollmentAdmin)
