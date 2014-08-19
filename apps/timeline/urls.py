from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from timeline.views import TimeLineView, HomePageView

urlpatterns = patterns("",
    # all items
    url(r"^$", login_required(TimeLineView.as_view()), name="timeline"),
    url(r"^homepage$", "timeline.views.home", name="timeline_homepage"),
    url(r"^legacy$", "timeline.views.legacy", name="5c_homepage"),
)
