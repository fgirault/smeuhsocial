#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import urlize

from friends.models import friend_set_for
from microblogging.models import Tweet
from pinax.apps.photos.models import Image
from threadedcomments.models import ThreadedComment

ITEMS_PER_FEED = getattr(settings, 'PINAX_ITEMS_PER_FEED', 20)

class AllTweet(Feed):
    title = "Touites MySmeuh"
    link = "/tweets/all"
    description = "Tous les touites de MySmeuh"

    def items(self, user):
        return Tweet.objects.order_by('-sent')[:ITEMS_PER_FEED]

    def item_title(self, item):
        return "Touite de %s" % item.sender.username

    def item_description(self, item):
        return urlize(item.text)

    def item_pub_date(self, item):
        return item.sent

class UserTweet(Feed):

    def get_object(self, request, username):
        return get_object_or_404(User, username=username)

    def link(self, user):
        return "/%s/" % user.username

    def title(self, user):
        return "Touites de %s" % user.username

    def description(self, user):
        return "Les touites de %s sur MySmeuh" % user.username

    def items(self, user):
        return Tweet.objects.filter(sender_id=user.id, sender_type=ContentType.objects.get_for_model(user)).order_by("-sent")[:ITEMS_PER_FEED]

    def item_title(self, item):
        return "Touite de %s" % item.sender.username

    def item_description(self, item):
        return item.text

    def item_pub_date(self, item):
        return item.sent

class UserTweetWithFriends(UserTweet):

    def title(self, user):
        return "Touites de %s et ses amis" % user.username

    def description(self, user):
        return "Les touites de %s et ses amis sur MySmeuh" % user.username

    def items(self, user):
        friends = friend_set_for(user)
        friend_ids = [friend.id for friend in friends] + [user.id]
        return Tweet.objects.filter(sender_id__in=friend_ids, sender_type__name="user")


class AllPhotos(Feed):
    title = "Photos MySmeuh"
    link = "/photos"
    descriptions = u"Les dernières photos postées sur MySmeuh"

    def items(self):
        return Image.objects.filter(is_public=True).order_by("-date_added")[:ITEMS_PER_FEED]

    def item_title(self, item):
        return u'« %s » par %s' % (item.title, item.member.username)

    def item_description(self, item):
        return u'<img src="%s"><p>%s</p>' % (item.get_display_url(),
                urlize(item.caption))

    def item_pub_date(self, item):
        return item.date_added

class AllComments(Feed):
    title = "Commentaires MySmeuh"
    link = "/"
    description = u"Les derniers commentaires postés sur MySmeuh"

    def items(self):
        return ThreadedComment.objects.order_by('-date_submitted')[:ITEMS_PER_FEED]

    def item_title(self, item):
        try:
            return u'%s à propos de « %s »' % (item.user, item.content_object.title)
        except:
            return u'%s à propos d\'un contenu supprimmé' % item.user

    def item_description(self, item):
        return urlize(item.comment)

    def item_pub_date(self, item):
        return item.date_submitted

    def item_link(self, item):
        try:
            return item.content_object.get_absolute_url()
        except:
            return "/"
