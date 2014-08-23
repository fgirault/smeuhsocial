from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

urlpatterns = patterns("",
    # all items
    url(r"^$", "artist.views.index", name="artist_index"),   
)
