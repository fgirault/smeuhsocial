from django.import template

register = template.Library()

@register.simple_tag
def profile_link():
    return 'aaa'
