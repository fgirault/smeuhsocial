from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from pinax.apps.blog.models import Post



class BlogForm(forms.ModelForm):
    
    slug = forms.SlugField(
        max_length = 40,
        help_text = _("a short version of the title consisting only of letters, numbers, underscores and hyphens."),
    )
    
    class Meta:
        model = Post
        exclude = [
            "author",
            "creator_ip",
            "created_at",
            "updated_at",
            "publish",
        ]
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(BlogForm, self).__init__(*args, **kwargs)
    
    def clean_slug(self):
        if not self.instance.pk:
            if Post.objects.filter(author=self.user, slug=self.cleaned_data["slug"]).exists():
                raise forms.ValidationError(u"This field must be unique")
            return self.cleaned_data["slug"]
        try:
            post = Post.objects.get(
                author = self.user,
                created_at__month = self.instance.created_at.month,
                created_at__year = self.instance.created_at.year,
                slug = self.cleaned_data["slug"]
            )
            if post != self.instance:
                raise forms.ValidationError(u"This field must be unique")
        except Post.DoesNotExist:
            pass
        return self.cleaned_data["slug"]
