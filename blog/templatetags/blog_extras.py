"""
这里我们首先导入 template 这个模块，然后实例化了一个 template.Library 类，
并将函数 show_recent_posts 装饰为 register.inclusion_tag，这样就告诉 django，
这个函数是我们自定义的一个类型为 inclusion_tag 的模板标签。
"""

from django import template
from ..models import Post, Category, Tag
from django.db.models.aggregates import Count

register = template.Library()

@register.inclusion_tag('blog/inclusions/_recent_posts.html', takes_context=True)
def show_recent_posts(context, num=5):
    return {
        'recent_post_list': Post.objects.all()[:num],
    }

@register.inclusion_tag('blog/inclusions/_archives.html', takes_context=True)
def show_archives(context):
    return {
        'date_list': Post.objects.dates('created_time', 'month', order='DESC'),
    }

@register.inclusion_tag('blog/inclusions/_categories.html', takes_context=True)
def show_categories(context):
    category_list = Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    return {
        # 'category_list': Category.objects.all(),
        'category_list': category_list,
    }

@register.inclusion_tag('blog/inclusions/_tags.html', takes_context=True)
def show_tags(context):
    tag_list = Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    return {
        # 'tag_list': Tag.objects.all(),
        'tag_list': tag_list,
    }
