"""

views for the mysmeuh timeline application.
"""
import datetime

from django.views.generic import TemplateView #, RedirectView
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

# model import
from microblogging.models import Tweet
from photos.models import Image
from audiotracks.models import Track
from blog.models import Post
from threadedcomments.models import ThreadedComment
        
class TimeLineItem(object):
    """
    A wrapping class over a content to be displayed in the timeline
    """    
    def __init__(self, item, date, user, template):
        """
        
        @param item: an object to be displayed in the timeline (tweet, 
            image, comment, post, track ...)
        @param date: the datetime of the item
        @param user: original poster
        @param template:  
        """        
        self.item = item
        self.date = date
        self.user = user
        self.template = template           

class TimeLineView(TemplateView):

    template_name = "timeline/index.html"

    def get_context_data(self, **kwargs):
        context = super(TimeLineView, self).get_context_data(**kwargs)
        # TODO use a query parameter for the time delta. here is 3 months
        ago = datetime.datetime.now() - datetime.timedelta(30 * 3)
                        
        tweets = [ 
            TimeLineItem(item, item.sent, item.sender, "timeline/_tweet.html") 
            for item in Tweet.objects.all().filter(sent__gte=ago).order_by("-sent")
            ]            
                
        posts =  [ 
            TimeLineItem(item, item.publish, item.author, "timeline/_post.html") 
            for item in Post.objects.all().filter(publish__gte=ago, status = 2).order_by("-publish")
            ]
               
        images = [ 
            TimeLineItem(item, item.date_added, item.member, "timeline/_photo.html") 
            for item in Image.objects.all().filter(is_public = True).filter(date_added__gte=ago).order_by("-date_added")
            ]
        
        tracks = [ 
            TimeLineItem(item, item.updated_at, item.user, "timeline/_track.html") 
            for item in Track.objects.all().filter(updated_at__gte=ago).order_by("-updated_at")
            ]
        
        comments = [ 
            TimeLineItem(item, item.date_submitted, item.user, "timeline/_comment.html") 
            for item in ThreadedComment.objects.all().filter(date_submitted__gte=ago).order_by("-date_submitted")
            ]
        
        items = merge(tweets, images, posts, tracks, comments, field="date")
        
        context['timelineitems'] = items                
        context['posts'] = posts
        context['prefix_sender'] = True
        return context
        
def merge_lists(left, right, field=None):
    i, j = 0, 0
    result = []
    while (i < len(left) and j < len(right)):
        if getattr(left[i], field) >= getattr(right[j], field):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def merge(*querysets, **kwargs):
    field = kwargs.get('field')
    if field is None:
        raise TypeError('you need to provide a key to do comparisons on')
    if len(querysets) == 1:
        return querysets[0]
    
    qs = [list(x) for x in querysets]
    q1, q2 = qs.pop(), qs.pop()
    result = merge_lists(q1, q2, field)
    for q in qs:
        result = merge_lists(result, q, field)
    return result        
    
class HomePageView(TimeLineView):
    
    template_name = "timeline/homepage/homepage.html"
    
    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        # reduce the timeline items
        context['timelineitems'] = context['timelineitems'][:16]
        context['latest_photos'] = Image.objects.all().order_by("-date_added")[:16]
        context['latest_blogs'] = Post.objects.all().filter(status = 2).order_by("-publish")[:10]
        context['latest_tracks'] = Track.objects.all().order_by("-created_at")[:6]        
        return context

# old stuff extracted from the main urls.py file, to run the 5 column home page
class LegacyHomePageView(TemplateView):

    template_name = "timeline/homepage/legacy.html"

    def get_context_data(self, **kwargs):
        context = super(LegacyHomePageView, self).get_context_data(**kwargs)
        context['latest_tweets'] = lambda: Tweet.objects.all().order_by(
            "-sent")[:12]
        context['latest_blogs'] = lambda: Post.objects.filter(
            status=2).order_by("-publish")[:10]
        context['latest_photos'] = lambda: Image.objects.all().order_by(
            "-date_added")[:18]
        context['latest_tracks'] = lambda: Track.objects.all().order_by(
            "-created_at")[:6]
        context['prefix_sender'] = True
        return context

    
home = login_required(HomePageView.as_view())

legacy = LegacyHomePageView.as_view()

    