# Create your views here.

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User

from tagging.models import Tag
from tagging.utils import calculate_cloud, LOGARITHMIC
from pinax.apps.blog.models import Post

def tag_index(request, template_name="tagging_ext/index.html", min_size=0, limit=100):
    query = """
        SELECT tag_item.tag_id as tag_id, COUNT(tag_item.tag_id) as counter 
        FROM tagging_taggeditem as tag_item 
        INNER JOIN tagging_tag as tag ON (tag.id = tag_item.tag_id)
        GROUP BY tag.name,tag_id
        HAVING COUNT(tag.name) > %s
        ORDER BY tag.name
        LIMIT %s
    """

    cursor = connection.cursor()
    cursor.execute(query, [min_size, limit])

    tags = []

    for row in cursor.fetchall():
        try:
            tag = Tag.objects.get(id=row[0])
        except ObjectDoesNotExist:
            continue
            
        if ' ' in tag.name:
            continue
        
        tag.count = row[1]
        tags.append(tag)    

    tags = calculate_cloud(tags, steps=5, distribution=LOGARITHMIC)
        
    return render_to_response(template_name, {'tags': tags},
        context_instance=RequestContext(request))


def user_blog_index(request, username, template_name="blog/user_blog.html"):
    blogs = Post.objects.filter(status=2).select_related(depth=1).order_by("-publish")
    if username is not None:
        user = get_object_or_404(User, username=username.lower())
        blogs = blogs.filter(author=user)
    return render_to_response(template_name, {
        "blogs": blogs,
        "username": username,
    }, context_instance=RequestContext(request))
