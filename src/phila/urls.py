from django.conf.urls import url


def get_strrep(request):
    """
    Return the string representation of any model object. Used to quickly get
    object names for raw ID fields in the admin interface.

    """
    ctype_string = request.GET['contenttype']
    object_id = request.GET['id']

    from django.contrib.contenttypes.models import ContentType
    ctype_app, ctype_model = ctype_string.split('.')
    ctype = ContentType.objects.get_by_natural_key(ctype_app, ctype_model)
    obj = ctype.get_object_for_this_type(id=object_id)

    from django.http import HttpResponse
    from django.core.urlresolvers import reverse
    # TODO: Ensure that the user has permission to affect the given change. If
    #       the current user doesn't have change permission, they probably
    #       shouldn't be able to even see the string representation.
    link_text = ('<a id="{app}_{model}_{objid}_edit_link" href="{url}" '
                 'onclick="showAdminPopup(this, \'nosuchfield\');" '
                 'target="_blank">{repr}</a>')
    return HttpResponse(link_text.format(
        app=ctype_app,
        model=ctype_model,
        objid=obj.id,
        url=reverse('admin:{}_{}_change'.format(ctype_app, ctype_model), args=(obj.id,)),
        repr=obj))


urlpatterns = [
    url(r'^get-strrep$', get_strrep),
]
