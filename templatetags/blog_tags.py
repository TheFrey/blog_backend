from django import template
from ..models import Post
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))


@register.simple_tag
def total_posts():
    return Post.objects.filter(status="published").count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.objects.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}
