from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to

from django.contrib import admin
admin.autodiscover()

from microblogging.feeds import TweetFeedAll, TweetFeedUser, TweetFeedUserWithFriends
from microblogging.models import Tweet
from tagging.models import TaggedItem

from pinax.apps.account.openid_consumer import PinaxConsumer
from pinax.apps.blog.feeds import BlogFeedAll, BlogFeedUser
from pinax.apps.blog.models import Post
from pinax.apps.photos.models import Image
from pinax.apps.topics.models import Topic
from pinax.apps.blog.forms import BlogForm
from audiotracks.models import Track
from smeuhoverride import feeds


handler500 = "pinax.views.server_error"


tweets_feed_dict = {"feed_dict": {
    "all": TweetFeedAll,
    "only": TweetFeedUser,
    "with_friends": TweetFeedUserWithFriends,
}}

blogs_feed_dict = {"feed_dict": {
    "all": BlogFeedAll,
    "only": BlogFeedUser,
}}

urlpatterns = patterns("",
    url(r"^favicon.ico/?$", redirect_to, {'url': settings.STATIC_URL + 'img/favicon.ico' }),
    url(r"^$", direct_to_template, {
        "template": "homepage.html",
        "extra_context": {
            "latest_tweets": lambda: Tweet.objects.all().order_by("-sent")[:12],
            "latest_blogs": lambda: Post.objects.filter(status=2).order_by("-publish")[:10],
            "latest_photos": lambda: Image.objects.all().order_by("-date_added")[:18],
            "latest_tracks": lambda: Track.objects.all().order_by("-created_at")[:6],
            "prefix_sender": True,
            }
    }, name="home"),
    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^openid/(.*)", PinaxConsumer()),
    url(r"^profiles/", include("pinax.apps.profiles.urls")),
    url(r"^bbauth/", include("pinax.apps.bbauth.urls")),
    url(r"^authsub/", include("pinax.apps.authsub.urls")),

    # Blog URLs ####################################################

    # all blog posts
    url(r"^blogs/?$", "pinax.apps.blog.views.blogs", name="blog_list_all"),
 
    url(r"^(?P<username>[\w\._-]+)/blog/feed/?$", feeds.UserBlogPosts(),
            name="user_blog_feed"),

    # blog post
    url(r"^(?P<username>[-\w]+)/blog/(?P<slug>[-\w]+)/source/?$",
        "smeuhoverride.views.blog_post_source", name="blog_post_source"),
    url(r"^(?P<username>[-\w]+)/blog/(?P<slug>[-\w]+)/?$", "pinax.apps.blog.views.post", name="blog_post"),
    
    # blog post for user
    url(r"^(?P<username>\w+)/blog/?$", "smeuhoverride.views.user_blog_index", name="blog_list_user"),
    
    # your posts
    url(r"^blogs/your_posts/?$", "pinax.apps.blog.views.your_posts", name="blog_list_yours"),
    
    # new blog post
    url(r"^blogs/new/$", "pinax.apps.blog.views.new", name="blog_new"),
    
    # edit blog post
    url(r"^blogs/edit/(\d+)/$", "pinax.apps.blog.views.edit", name="blog_edit"),
    
    #destory blog post
    url(r"^blogs/destroy/(\d+)/$", "pinax.apps.blog.views.destroy", name="blog_destroy"),
    
    # ajax validation
    (r"^blogs/validate/$", "ajax_validation.views.validate", {
        "form_class": BlogForm,
        "callback": lambda request, *args, **kwargs: {"user": request.user}
    }, "blog_form_validate"),

    # /END Blog URLs ###################################################

    url(r"^invitations/", include("friends_app.urls")),
    url(r"^notices/", include("notification.urls")),
    url(r"^messages/", include("messages.urls")),
    url(r"^announcements/", include("announcements.urls")),
    url(r"^touites/", include("microblogging.urls")),
    url(r"^comments/", include("threadedcomments.urls")),
    url(r"^i18n/", include("django.conf.urls.i18n")),
    url(r"^photos/details/(?P<id>\d+)/$", "smeuhoverride.views.photo_details", name="photo_details"),
    url(r"^photos/", include("pinax.apps.photos.urls")),
    url(r"^avatar/", include("avatar.urls")),
    url(r"^flag/", include("flag.urls")),
    url(r"^feeds/touites/(?P<username>[\w\._-]+)/with_friends/?$",
            feeds.UserTweetWithFriends(), name="user_friends_tweets"),
    url(r"^feeds/touites/(?P<username>[\w\._-]+)/?$", feeds.UserTweet(),
            name="user_tweets"),
    url(r"^feeds/touites/?$", feeds.AllTweet(), name="all_tweets_feed"),
    url(r"^feeds/photos/?$", feeds.AllPhotos(), name="all_photos_feed"),
    url(r"^feeds/comments/?$", feeds.AllComments(), name="all_comments_feed"),
    url(r"^feeds/blogs/?$", feeds.AllBlogPosts(), name="all_blogs_feed"),
)

## @@@ for now, we'll use friends_app to glue this stuff together

friends_photos_kwargs = {
    "template_name": "photos/friends_photos.html",
    "friends_objects_function": lambda users: Image.objects.filter(is_public=True, member__in=users),
}

friends_blogs_kwargs = {
    "template_name": "blog/friends_posts.html",
    "friends_objects_function": lambda users: Post.objects.filter(author__in=users),
}

friends_tweets_kwargs = {
    "template_name": "microblogging/friends_tweets.html",
    "friends_objects_function": lambda users: Tweet.objects.filter(sender_id__in=[user.id for user in users], sender_type__name="user"),
}

urlpatterns += patterns("",
    url(r"^photos/friends_photos/$", "friends_app.views.friends_objects", kwargs=friends_photos_kwargs, name="friends_photos"),
    url(r"^blog/friends_blogs/$", "friends_app.views.friends_objects", kwargs=friends_blogs_kwargs, name="friends_blogs"),
    url(r"^touites/friends_tweets/$", "friends_app.views.friends_objects", kwargs=friends_tweets_kwargs, name="friends_tweets"),
)

tagged_models = (
    dict(title="Blog Posts",
        query=lambda tag : TaggedItem.objects.get_by_model(Post, tag).filter(status=2),
        content_template="pinax_tagging_ext/blogs.html",
    ),
    dict(title="Photos",
        query=lambda tag: TaggedItem.objects.get_by_model(Image, tag).filter(safetylevel=1),
        content_template="pinax_tagging_ext/photos.html",
    ),
    dict(title="Audio Tracks",
        query=lambda tag: TaggedItem.objects.get_by_model(Track, tag),
        content_template="pinax_tagging_ext/audiotracks.html",
    ),
    dict(title="Topics",
        query=lambda tag: TaggedItem.objects.get_by_model(Topic, tag),
    ),
)
tagging_ext_kwargs = {
    "tagged_models": tagged_models,
}

urlpatterns += patterns("",
    url(r"^tags/(?P<tag>.+)/(?P<model>.+)$", "tagging_ext.views.tag_by_model",
        kwargs=tagging_ext_kwargs, name="tagging_ext_tag_by_model"),
    url(r"^tags/(?P<tag>.+)/$", "tagging_ext.views.tag",
        kwargs=tagging_ext_kwargs, name="tagging_ext_tag"),
    url(r"^tags/$", "smeuhoverride.views.tag_index", kwargs={'limit': 1000}, name="tagging_ext_index"),
)

urlpatterns += patterns("",
        url("^(?P<username>[\w\._-]+)/music", include("audiotracks.urls")),
        url("^music", include("audiotracks.urls"))
        )

urlpatterns += patterns("",
    url(r"^(?P<username>[\w\._-]+)/$", "pinax.apps.profiles.views.profile", name="profile_detail"),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
