# Create your views here.

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.http import Http404, get_host, HttpResponse

from tagging.models import Tag
from tagging.utils import calculate_cloud, LOGARITHMIC
from pinax.apps.blog.models import Post
from pinax.apps.photos.views import group_and_bridge, group_context
from pinax.apps.photos.models import Image

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


def blog_post_source(request, username, slug):
    post = get_object_or_404(Post, slug=slug,
        author__username=username)

    if post.status == 1 and post.author != request.user:
        raise Http404

    return HttpResponse(post.body, mimetype="text/plain; charset=utf-8")



def get_first_id_or_none(objects):
    try:
        return objects[0].id
    except IndexError:
        return None


def photo_details(request, id, template_name="photos/details.html"):
    """
    show the photo details
    """

    group, bridge = group_and_bridge(request)
    
    photos = Image.objects.all()
    
    if group:
        photos = group.content_objects(photos, join="pool", gfk_field="content_object")
    else:
        photos = photos.filter(pool__object_id=None)
    
    photo = get_object_or_404(photos, id=id)

    previous_photo_id = get_first_id_or_none(
            photos.filter(id__lt=photo.id, is_public=True).order_by('-id'))
    next_photo_id = get_first_id_or_none(photos.filter(id__gt=photo.id,
        is_public=True).order_by('id'))
    
    # @@@: test
    if not photo.is_public and request.user != photo.member:
        raise Http404
    
    photo_url = photo.get_display_url()
    
    host = "http://%s" % get_host(request)
    
    if photo.member == request.user:
        is_me = True
    else:
        is_me = False
    
    ctx = group_context(group, bridge)
    ctx.update({
        "host": host,
        "photo": photo,
        "photo_url": photo_url,
        "is_me": is_me,
        "previous_photo_id": previous_photo_id,
        "next_photo_id": next_photo_id,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))
