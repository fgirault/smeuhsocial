from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.utils.translation  import ugettext_lazy as _
from tagging.fields import TagField
from tagging.models import TaggedItem
from audiotracks.models import AbstractTrack


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


class Track(AbstractTrack):

    class Meta:
        db_table = 'audiotracks_track'

    tags = TagField(_("Tags"))


