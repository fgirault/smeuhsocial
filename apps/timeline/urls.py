from django.conf.urls import patterns, url

urlpatterns = patterns("",
    # all items
    url(r"^$", "timeline.views.timeline", name="timeline"),
    url(r"^homepage$", "timeline.views.home", name="timeline_homepage"),
    url(r"^legacy$", "timeline.views.legacy", name="5c_homepage"),
    url(r"^friends$", "timeline.views.friends", name="friends_news"),
    url(r"^following$", "timeline.views.following", name="following_news"),
    url(r"^user/home/(?P<username>[\w\._-]+)/$", "timeline.views.user_home", name="user_homepage"),
    url(r"^user/(?P<username>[\w\._-]+)/$", "timeline.views.user_home", name="user_timeline"),
)
