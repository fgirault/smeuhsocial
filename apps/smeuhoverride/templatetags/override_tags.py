#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from microblogging.templatetags import microblogging_tags
from django import template

register = template.Library()

@register.simple_tag
def render_tweet_text(tweet):
    """
    Override render_tweet_text from microblogging to make URLs clickable
    """
    text = microblogging_tags.render_tweet_text(tweet)
    text = template.defaultfilters.urlize(text)
    return text

@register.inclusion_tag("_user_link.html")
def profile_link(member):
    return {'member': member}
