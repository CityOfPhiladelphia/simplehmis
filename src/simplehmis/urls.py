"""simplehmis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin


def get_strrep(request):
    ctype_string = request.GET['contenttype']
    object_id = request.GET['id']

    from django.contrib.contenttypes.models import ContentType
    ctype_app, ctype_model = ctype_string.split('.')
    ctype = ContentType.objects.get_by_natural_key(ctype_app, ctype_model)
    obj = ctype.get_object_for_this_type(id=object_id)

    from django.http import HttpResponse
    from django.core.urlresolvers import reverse
    # TODO: ensure that the user has permission to affect the given change.
    return HttpResponse('<a href="{}" target="_blank">{}</a>'.format(
        reverse('admin:{}_{}_change'.format(ctype_app, ctype_model), args=(obj.id,)), obj))


urlpatterns = [
    url(r'^get-strrep$', get_strrep),
    url(r'^', include(admin.site.urls)),
]
