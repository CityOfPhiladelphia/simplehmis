from django.utils.translation import ugettext as _
from django.forms.models import ModelForm, BaseInlineFormSet
from django.forms import ValidationError
from django.contrib.auth import get_user_model


class RequiredInlineFormSet(BaseInlineFormSet):
    """
    Generates an inline formset that is required
    """

    def _construct_form(self, i, **kwargs):
        """
        Override the method to change the form attribute empty_permitted
        """
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form


class HouseholdMemberFormset (RequiredInlineFormSet):
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


class PasswordlessUserCreationForm(ModelForm):
    """
    A form that creates a user, with no privileges and no password, from
    the given username.
    """

    class Meta:
        model = get_user_model()
        fields = ("username",)
