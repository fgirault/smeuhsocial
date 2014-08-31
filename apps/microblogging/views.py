from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from microblogging.utils import twitter_account_for_user, twitter_verify_credentials
from microblogging.models import Tweet, TweetInstance, Following, get_following_followers_lists
from microblogging.forms import TweetForm


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

def personal(request, form_class=TweetForm,
        template_name="microblogging/personal.html", success_url=None):
    """
    just the tweets the current user is following
    """
    
    twitter_account = twitter_account_for_user(request.user)
    
    following_list, followers_list = get_following_followers_lists(request.user)
    
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            tweet = form.save()
            if request.POST.get("pub2twitter", False):
                twitter_account.PostUpdate(text)
            if request.is_ajax():
                return HttpResponse("ok")
            else:
                if success_url is None:
                    success_url = reverse('microblogging.views.personal')
                return HttpResponseRedirect(success_url)
        reply = None
    else:
        reply = request.GET.get("reply", None)
        form = form_class()
        if reply:
            form.fields['text'].initial = u"@%s " % reply
    tweets = TweetInstance.objects.tweets_for(request.user).order_by("-sent")
    return render_to_response(template_name, {
        "form": form,
        "reply": reply,
        "tweets": tweets,
        "twitter_authorized": twitter_verify_credentials(twitter_account),
        "following_list": following_list,   
        "followers_list": followers_list
    }, context_instance=RequestContext(request))
personal = login_required(personal)

@login_required
def post_tweet(request, form_class=TweetForm, success_url=None):
    if request.method == "POST":
        twitter_account = twitter_account_for_user(request.user)
        form = form_class(request.user, request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            tweet = form.save()
            if request.POST.get("pub2twitter", False):
                twitter_account.PostUpdate(text)
            if request.is_ajax():
                return render_to_response('microblogging/_tweet.html', { 'tweet': tweet})                
            else:
                if success_url is None:
                    success_url = reverse('timeline.views.home')
                return HttpResponseRedirect(success_url)        
    
def public(request, template_name="microblogging/public.html"):
    """
    all the tweets
    """
    tweets = Tweet.objects.all().order_by("-sent")
    following_list, followers_list = get_following_followers_lists(request.user)

    return render_to_response(template_name, {
        "tweets": tweets,
        "following_list": following_list,   
        "followers_list": followers_list
    }, context_instance=RequestContext(request))

def single(request, id, template_name="microblogging/single.html"):
    """
    A single tweet.
    """
    tweet = get_object_or_404(Tweet, id=id)
    return render_to_response(template_name, {
        "tweet": tweet,
    }, context_instance=RequestContext(request))


def toggle_follow(request, username):
    """
    Either follow or unfollow a user.
    """
    other_user = get_object_or_404(User, username=username)
    if request.user == other_user:
        is_me = True
    else:
        is_me = False
    if request.user.is_authenticated() and request.method == "POST" and not is_me:
        if request.POST["action"] == "follow":
            Following.objects.follow(request.user, other_user)
            messages.success(request, _("You are now following %(other_user)s") % {'other_user': other_user})
            if notification:
                notification.send([other_user], "tweet_follow", {"user": request.user})
        elif request.POST["action"] == "unfollow":
            Following.objects.unfollow(request.user, other_user)
            messages.success(request, _("You have stopped following %(other_user)s") % {'other_user': other_user})
    return HttpResponseRedirect(reverse("profile_detail", args=[other_user]))

