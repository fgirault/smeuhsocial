"""

views for the mysmeuh timeline application.
"""
import datetime

from django.views.generic import TemplateView #, RedirectView
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect

# model import
from microblogging.models import Tweet
from photos.models import Image
from audiotracks.models import Track
from blog.models import Post
from threadedcomments.models import ThreadedComment
from friends.models import friend_set_for
from microblogging.models import get_following_followers_lists
from friends.forms import InviteFriendForm
from friends.models import FriendshipInvitation, Friendship
from microblogging.models import Following
from django.db.transaction import is_managed
        
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
        ago = datetime.datetime.now() - datetime.timedelta(30)
                        
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

class FriendsPageView(TemplateView):
    
    template_name = "timeline/friends.html"
    
    def get_context_data(self, **kwargs):
        context = super(FriendsPageView, self).get_context_data(**kwargs)
        # TODO use a query parameter for the time delta. here is 3 months
        ago = datetime.datetime.now() - datetime.timedelta(30)
        friends = friend_set_for(self.request.user)
                                      
        tweets = [ 
            TimeLineItem(item, item.sent, item.sender, "timeline/_tweet.html") 
            for item in Tweet.objects.all().filter(sent__gte=ago, sender_id__in=[user.id for user in friends], sender_type__name="user").order_by("-sent")
            ]            
                
        posts =  [ 
            TimeLineItem(item, item.publish, item.author, "timeline/_post.html") 
            for item in Post.objects.all().filter(publish__gte=ago, status = 2, author__in=friends).order_by("-publish")
            ]
               
        images = [ 
            TimeLineItem(item, item.date_added, item.member, "timeline/_photo.html") 
            for item in Image.objects.all().filter(is_public = True).filter(date_added__gte=ago, member__in=friends).order_by("-date_added")
            ]
        
        tracks = [ 
            TimeLineItem(item, item.updated_at, item.user, "timeline/_track.html") 
            for item in Track.objects.all().filter(updated_at__gte=ago, user__in=friends).order_by("-updated_at")
            ]
        
        comments = [ 
            TimeLineItem(item, item.date_submitted, item.user, "timeline/_comment.html") 
            for item in ThreadedComment.objects.all().filter(date_submitted__gte=ago, user__in=friends).order_by("-date_submitted")
            ]
        
        items = merge(tweets, images, posts, tracks, comments, field="date")
        
        context['timelineitems'] = items        
        context['prefix_sender'] = True        
        return context

class FollowingPageView(TemplateView):
    
    template_name = "timeline/following.html"
    
    def get_context_data(self, **kwargs):
        context = super(FollowingPageView, self).get_context_data(**kwargs)
        # TODO use a query parameter for the time delta. here is 3 months
        ago = datetime.datetime.now() - datetime.timedelta(30)
        following_list, followers_list = get_following_followers_lists(self.request.user)
                              
        tweets = [ 
            TimeLineItem(item, item.sent, item.sender, "timeline/_tweet.html") 
            for item in Tweet.objects.all().filter(sent__gte=ago, sender_id__in=[user.id for user in following_list], sender_type__name="user").order_by("-sent")
            ]            
                
        posts =  [ 
            TimeLineItem(item, item.publish, item.author, "timeline/_post.html") 
            for item in Post.objects.all().filter(publish__gte=ago, status = 2, author__in=following_list).order_by("-publish")
            ]
               
        images = [ 
            TimeLineItem(item, item.date_added, item.member, "timeline/_photo.html") 
            for item in Image.objects.all().filter(is_public = True).filter(date_added__gte=ago, member__in=following_list).order_by("-date_added")
            ]
        
        tracks = [ 
            TimeLineItem(item, item.updated_at, item.user, "timeline/_track.html") 
            for item in Track.objects.all().filter(updated_at__gte=ago, user__in=following_list).order_by("-updated_at")
            ]
        
        comments = [ 
            TimeLineItem(item, item.date_submitted, item.user, "timeline/_comment.html") 
            for item in ThreadedComment.objects.all().filter(date_submitted__gte=ago, user__in=following_list).order_by("-date_submitted")
            ]
        
        items = merge(tweets, images, posts, tracks, comments, field="date")
        
        context['timelineitems'] = items                        
        context['prefix_sender'] = True        
        return context

class UserHomePageView(TemplateView):
    
    template_name = "timeline/homepage/user.html"
    
    def get_context_data(self, **kwargs):
        context = super(UserHomePageView, self).get_context_data(**kwargs)
        # TODO use a query parameter for the time delta. here is 3 months
        ago = datetime.datetime.now() - datetime.timedelta(30 * 3)
        following_list, followers_list = get_following_followers_lists(self.request.user)
        other_friends = None
        username = name = context.get('username', None)                         
        
        if name:
            user = other_user = get_object_or_404(User, username=name)
        else:
            user = other_user = self.request.user
            
        if self.request.user == other_user:
            context['is_me']= True
            is_friend = False
        else:
            is_friend = context['is_friend'] = Friendship.objects.are_friends(self.request.user, other_user)
            context['is_following'] = Following.objects.is_following(self.request.user, other_user)
        context['other_friends'] = Friendship.objects.friends_for_user(other_user)
                     
            
        context['other_user'] = other_user
        tweets = [ 
            TimeLineItem(item, item.sent, item.sender, "timeline/_tweet.html") 
            for item in Tweet.objects.all().filter(sender_id=user.id, sender_type__name="user").order_by("-sent")[:16]
            ]            
        
        context['latest_blogs'] = Post.objects.all().filter(status = 2, author=user).order_by("-publish")[:10]
        
        posts =  [ 
            TimeLineItem(item, item.publish, item.author, "timeline/_post.html") 
            for item in context['latest_blogs']
            ]
               
        context['latest_photos'] = Image.objects.all().filter(is_public = True, member=user).order_by("-date_added")[:16]
               
        images = [ 
            TimeLineItem(item, item.date_added, item.member, "timeline/_photo.html") 
            for item in context['latest_photos']
            ]
        
        context['latest_tracks'] = Track.objects.all().filter(user=user).order_by("-updated_at")[:6]
        
        tracks = [ 
            TimeLineItem(item, item.updated_at, item.user, "timeline/_track.html") 
            for item in context['latest_tracks']
            ]
        
        comments = [ 
            TimeLineItem(item, item.date_submitted, item.user, "timeline/_comment.html") 
            for item in ThreadedComment.objects.all().filter(user = user).order_by("-date_submitted")[:16]
            ]        
        
        context['timelineitems'] = merge(tweets, comments, field="date")[:16]                 
        context['prefix_sender'] = True
        
        
        invite_form = None
        if is_friend:
            previous_invitations_to = None
            previous_invitations_from = None
            if self.request.method == "POST":
                if self.request.POST.get("action") == "remove": # @@@ perhaps the form should just post to friends and be redirected here
                    Friendship.objects.remove(self.request.user, other_user)
                    messages.add_message(self.request, messages.SUCCESS,
                        ugettext("You have removed %(from_user)s from friends") % {
                            "from_user": other_user
                        }
                    )
                    is_friend = False
                    invite_form = InviteFriendForm(self.request.user, {
                        "to_user": username,
                        "message": ugettext("Let's be friends!"),
                    })
        
        else:
            if self.request.user.is_authenticated() and self.request.method == "POST":
                pass
            else:
                invite_form = InviteFriendForm(self.request.user, {
                    "to_user": username,
                    "message": ugettext("Let's be friends!"),
                })
                previous_invitations_to = None
                previous_invitations_from = None
        
        context['invite_form'] = invite_form
        context['previous_invitations_to'] = previous_invitations_to
        context['previous_invitations_from'] = previous_invitations_from  
        context['other_friends'] = other_friends               
        return context
    
    
    def post(self, *args, **kw):        
        if self.request.POST.get("action") == "invite": 
            username = self.request.POST.get("to_user")
            other_user = get_object_or_404(User, username=username)
            
            invite_form = InviteFriendForm(self.request.user, self.request.POST)
            if invite_form.is_valid():
                invite_form.save()
                messages.success(self.request, _("Friendship requested with %(username)s") % {
                    'username': invite_form.cleaned_data['to_user']
                })
        elif self.request.POST.get("action") == "remove":
            username = kw['username']
            other_user = get_object_or_404(User, username=username)
            Friendship.objects.remove(self.request.user, other_user)
            messages.add_message(self.request, messages.SUCCESS,
                ugettext("You have removed %(from_user)s from friends") % {
                    "from_user": other_user
                }
            )           
        else:
            username = kw['username']
            other_user = get_object_or_404(User, username=username)
            invite_form = InviteFriendForm(self.request.user, {
                "to_user": username,
                "message": ugettext("Let's be friends!"),
            })
            invitation_id = self.request.POST.get("invitation", None)
            if self.request.POST.get("action") == "accept":
                try:
                    invitation = FriendshipInvitation.objects.get(id=invitation_id)
                    if invitation.to_user == self.equest.user:
                        invitation.accept()
                        messages.add_message(self.request, messages.SUCCESS,
                            ugettext("You have accepted the friendship request from %(from_user)s") % {
                                "from_user": invitation.from_user
                            }
                        )
                except FriendshipInvitation.DoesNotExist:
                    pass
            elif self.request.POST.get("action") == "decline":
                try:
                    invitation = FriendshipInvitation.objects.get(id=invitation_id)
                    if invitation.to_user == self.request.user:
                        invitation.decline()
                        messages.add_message(self.request, messages.SUCCESS,
                            ugettext("You have declined the friendship request from %(from_user)s") % {
                                "from_user": invitation.from_user
                            }
                        )                        
                except FriendshipInvitation.DoesNotExist:
                    pass
        
        return HttpResponseRedirect(reverse("timeline.views.userhome", kwargs = {"username": username}))



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

friends = login_required(FriendsPageView.as_view())

following = login_required(FollowingPageView.as_view())

userhome = login_required(UserHomePageView.as_view())