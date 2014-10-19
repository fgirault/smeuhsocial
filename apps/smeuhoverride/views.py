# Create your views here.

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required

from tagging.models import Tag
from tagging.utils import calculate_cloud, LOGARITHMIC
from blog.models import Post
from photos.models import Image

class TagInTheCloud:
    """

    a fake Tag model to feed the cloud
    """
    def __init__(self, name, count, *args):
        self.name = name
        self.count = count

def tag_index(request, template_name="tagging_ext/index.html", *args, **kw):
    query = """
        SELECT tag.name as name, COUNT(tag_item.tag_id) as counter, tag_item.tag_id as tag_id
        FROM tagging_taggeditem as tag_item
        INNER JOIN tagging_tag as tag ON (tag.id = tag_item.tag_id)
        GROUP BY tag.name, tag_id
        ORDER BY tag.name
    """
    cursor = connection.cursor()
    cursor.execute(query)

    tags = calculate_cloud(
        [ TagInTheCloud(*row) for row in cursor ],
        steps=5,
        distribution=LOGARITHMIC
        )

    return render_to_response(template_name, {'tags': tags},
        context_instance=RequestContext(request))


def user_blog_index(request, username, template_name="blog/user_blog.html"):
    blogs = Post.objects.filter(status=2).select_related().order_by("-publish")
    if username is not None:
        user = get_object_or_404(User, username=username.lower())
        blogs = blogs.filter(author=user)
    return render_to_response(template_name, {
        "blogs": blogs,
        "username": username,
    }, context_instance=RequestContext(request))


def blog_post_source(request, username, slug):
    post = get_object_or_404(Post, slug=slug,
        author__username=username)

    if post.status == 1 and post.author != request.user:
        raise Http404

    return HttpResponse(post.body, content_type="text/plain; charset=utf-8")
