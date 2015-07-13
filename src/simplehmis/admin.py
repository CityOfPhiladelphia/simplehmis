from django.contrib import admin
from floppyforms.models import ModelForm
from . import models


class ClientAdmin (admin.ModelAdmin):
    form = ModelForm
    fieldsets = [
        ('Name', {'fields': ('first', 'middle', 'last', 'suffix', 'name_data_quality')}),
        ('Social Security', {'fields': ('ssn', 'ssn_data_quality')}),
        ('Date of Birth', {'fields': ('dob', 'dob_data_quality')}),
        (None, {'fields': ('gender', 'ethnicity', 'race', 'veteran_status')})
    ]

    list_display = ('name_display', 'dob_display', 'ssn_display')


admin.site.register(models.Organization)
admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Project)
admin.site.register(models.Enrollment)
