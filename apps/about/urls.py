from django.conf.urls import *
from django.views.generic import TemplateView


class WhatNextView(TemplateView):

    template_name = "about/what_next.html"


urlpatterns = patterns("",
    url(r"^what_next/$", WhatNextView.as_view())
)
