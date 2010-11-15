# Create your views here.
from smeuhmusic.models import Track
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

def index(request, username):
    tracks = Track.objects.all()
    return render_to_response("smeuhmusic/base.html", {'tracks': tracks}, 
            context_instance=RequestContext(request))

def create_track(request):
    title = request.POST.get('title')
    if title:
        track = Track(title=title, user=request.user)
        track.save()
    return redirect(reverse("smeuhmusic", args=[request.user]))

