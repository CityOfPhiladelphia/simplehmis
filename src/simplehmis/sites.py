from django.contrib.admin import AdminSite as BaseAdminSite
from django.shortcuts import render
from django.utils.translation import ugettext as _
from nopassword.forms import AuthenticationForm
from nopassword.models import LoginCode


class HMISAdminSite(BaseAdminSite):
    site_header = _('Philadelphia Simple HMIS')
    login_form = AuthenticationForm

    def login(self, request, extra_context=None):
        if request.method == 'POST':
            form = self.login_form(data=request.POST)
            if form.is_valid():
                code = LoginCode.objects.filter(user__username=request.POST.get('username'))[0]
                code.next = request.GET.get('next')
                code.save()
                code.send_login_code(
                    secure=request.is_secure(),
                    host=request.get_host(),
                )
                return render(request, 'registration/sent_mail.html')

        if request.method == 'GET':
            request.session.set_test_cookie()

        return super().login(request, extra_context=extra_context)
