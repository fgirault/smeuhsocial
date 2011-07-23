from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from tagging.models import TaggedItem

def taggeditem_delete(sender, **kwargs):
    """
    Deletes TaggedItems for ALL deleted model instances
    Workaround for bug:
        http://code.google.com/p/django-tagging/issues/detail?id=162
    """
    deleted = kwargs['instance']
    try:
        id = int(deleted.pk)
    except ValueError:
        return
    ctype = ContentType.objects.get_for_model(deleted)
    item_tags = TaggedItem.objects.filter(
            content_type=ctype,
            object_id=id,
        )
    item_tags.delete()

signals.post_delete.connect(taggeditem_delete)
