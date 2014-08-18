from django.conf.urls import patterns, url

from timeline.views import TimeLineView, HomePageView

urlpatterns = patterns("",
    # all items
    url(r"^$", "fukung.views.index", name="fukung"),
    url(r"^v/(?P<photo_id>\d+)/$", "fukung.views.view", name="fukung_view"),
)
