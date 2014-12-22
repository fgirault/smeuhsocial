from urllib import urlencode
from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.inclusion_tag("threadedcomments/comments.html", takes_context=True)
def comments(context, obj):
    qs_params = {"success_url": context["request"].get_full_path()}
    query_string = urlencode(qs_params)
    return {
        "object": obj,
        "request": context["request"],
        "user": context["user"],
        "acct_login_url": '?'.join([reverse('acct_login'), query_string])
    }
