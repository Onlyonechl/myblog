import markdown, re
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Tag
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.views.generic import ListView, DetailView
from pure_pagination.mixins import PaginationMixin
from django.contrib import messages
from django.db.models import Q

from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    CategorySerializer, PostHaystackSerializer, PostListSerializer, PostRetrieveSerializer, TagSerializer)
from rest_framework.serializers import DateField

from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.permissions import AllowAny

from rest_framework import viewsets
from rest_framework import mixins

from django_filters.rest_framework import DjangoFilterBackend
from .filters import PostFilter
from comments.serializers import CommentSerializer

from rest_framework_extensions.cache.decorators import cache_response

from rest_framework_extensions.key_constructor.bits import (
    ListSqlQueryKeyBit,
    PaginationKeyBit,
    RetrieveSqlQueryKeyBit,
)
from rest_framework_extensions.key_constructor.constructors import DefaultKeyConstructor

from .utils import UpdatedAtKeyBit

from rest_framework.throttling import AnonRateThrottle
from drf_haystack.viewsets import HaystackViewSet

# def index(request):
#     post_list = Post.objects.all()
#     return render(request, 'blog/index.html', context={'post_list': post_list})
class IndexView(PaginationMixin, ListView): # 由函数视图改成类视图
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 10    

def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    post.increase_views()

    # post.body = markdown.markdown(post.body, 
    #                                extensions=['markdown.extensions.extra', 
    #                                'markdown.extensions.codehilite',
    #                                'markdown.extensions.toc',   # 生成目录
    #                                ])

    # 和之前的代码不同，我们没有直接用 markdown.markdown() 方法来渲染 post.body 中的内容，
    # 而是先实例化了一个 markdown.Markdown 对象 md，和 markdown.markdown() 方法一样，也传入了 extensions 参数。
    # 接着我们便使用该实例的 convert 方法将 post.body 中的 Markdown 文本解析成 HTML 文本。
    # 而一旦调用该方法后，实例 md 就会多出一个 toc 属性，这个属性的值就是内容的目录，
    # 我们把 md.toc 的值赋给 post.toc 属性（要注意这个 post 实例本身是没有 toc 属性的，我们给它动态添加了 toc 属性，这就是 Python 动态语言的好处）。
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra', 
        'markdown.extensions.codehilite',
        #'markdown.extensions.toc',   # 生成目录
        TocExtension(slugify=slugify),  # 修改传给extentions的参数，美化目录标题的锚点URL
    ])
    post.body = md.convert(post.body)
    # 分析 toc 的内容，如果有目录结构，ul 标签中就有值，否则就没有值。我们可以使用正则表达式来测试 ul 标签中是否包裹有元素来确定是否存在目录。
    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    post.toc = m.group(1) if m is not None else ''

    return render(request, 'blog/detail.html', context={'post':post})

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        # 将文章阅读量 +1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()

        # 视图必须返回一个 HttpResponse 对象
        return response

#    def get_object(self, queryset=None):
#        # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
#        post = super().get_object(queryset=None)
#        md = markdown.Markdown(extensions=[
#            'markdown.extensions.extra',
#            'markdown.extensions.codehilite',
#            TocExtension(slugify=slugify),
#        ])
#        post.body = md.convert(post.body)
#
#        m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
#        post.toc = m.group(1) if m is not None else ''
#
#        return post


def archive(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    )
    return render(request, 'blog/index.html', context={'post_list': post_list})

# def category(request, pk):
#     cate = get_object_or_404(Category, pk=pk)
#     post_list = Post.objects.filter(category=cate)
#     return render(request, 'blog/index.html', context={'post_list': post_list})
class CategoryView(IndexView): # 直接继承IndexView
    # model = Post
    # template_name = 'blog/index.html'
    # context_object_name = 'post_list'
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)

def tag(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    post_list = Post.objects.filter(tag=tag)
    return render(request, 'blog/index.html', context={'post_list': post_list})

def categories(request):
    category_list = Category.objects.all()
    return render(request, 'blog/categories.html', context={'category_list': category_list})


def search(request):
    q = request.GET.get('q')

    if not q:
        error_msg = '请输入搜索关键词'
        messages.add_message(request, messages.ERROR, error_msg, extra_tags='danger')
        return redirect('blog:index')

    post_list = Post.objects.filter(Q(tittle__icontains=q)|Q(body__icontains=q))
    return render(request, 'blog/index.html', {'post_list':post_list})
    #如果用户输入了搜索关键词，我们就通过 filter 方法从数据库里过滤出符合条件的所有文章。这里的过滤条件是 title__icontains=q，
    #即 title 中包含（contains）关键字 q，前缀 i 表示不区分大小写。这里 icontains 是查询表达式（Field lookups），
    # 我们在之前也使用过其他类似的查询表达式，其用法是在模型需要筛选的属性后面跟上两个下划线。


# ---------------------------------------------------------------------------
#   Django REST framework 接口
# ---------------------------------------------------------------------------

class PostUpdatedAtKeyBit(UpdatedAtKeyBit):
    key = "post_updated_at"

class CommentUpdatedAtKeyBit(UpdatedAtKeyBit):
    key = "comment_updated_at"

class PostListKeyConstructor(DefaultKeyConstructor):
    list_sql = ListSqlQueryKeyBit()
    pagination = PaginationKeyBit()
    updated_at = PostUpdatedAtKeyBit()

class PostObjectKeyConstructor(DefaultKeyConstructor):
    retrieve_sql = RetrieveSqlQueryKeyBit()
    updated_at = PostUpdatedAtKeyBit()

class CommentListKeyConstructor(DefaultKeyConstructor):
    list_sql = ListSqlQueryKeyBit()
    pagination = PaginationKeyBit()
    updated_at = CommentUpdatedAtKeyBit()

class PostViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = PostListSerializer
    queryset = Post.objects.all()
    permission_classes = [AllowAny]
    serializer_class_table = {
      'list': PostListSerializer,
      'retrieve': PostRetrieveSerializer,
    }
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter

    def get_serializer_class(self):
        return self.serializer_class_table.get(
            self.action, super().get_serializer_class()
        )
    
    @action(
        methods=["GET"], 
        detail=False, 
        url_path="archive/dates", 
        url_name="archive-date",
    )
    def list_archive_dates(self, request, *args, **kwargs):
        dates = Post.objects.dates("created_time", "month", order="DESC")
        date_field = DateField()
        data = [date_field.to_representation(date) for date in dates]
        return Response(data=data, status=status.HTTP_200_OK)

    @cache_response(timeout=5 * 60, key_func=CommentListKeyConstructor())
    @action(
            methods=["GET"],
            detail=True,
            url_path="comments",
            url_name="comment",
            pagination_class=LimitOffsetPagination,
            serializer_class=CommentSerializer,
    )
    def list_comments(self, request, *args, **kwargs):
        # 根据 URL 传入的参数值（文章 id）获取到博客文章记录
        post = self.get_object()
        # 获取文章下关联的全部评论
        queryset = post.comment_set.all().order_by("-created_time")
        # 对评论列表进行分页，根据 URL 传入的参数获取指定页的评论
        page = self.paginate_queryset(queryset)
        # 序列化评论
        serializer = self.get_serializer(page, many=True)
        # 返回分页后的评论列表
        return self.get_paginated_response(serializer.data)

    @cache_response(timeout=5 * 60, key_func=PostListKeyConstructor())
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=5 * 60, key_func=PostObjectKeyConstructor())
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

index = PostViewSet.as_view({'get': 'list'})



class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    博客文章分类视图集

    list:
    返回博客文章分类列表
    """

    serializer_class = CategorySerializer
    # 关闭分页
    pagination_class = None

    def get_queryset(self):
        return Category.objects.all().order_by("name")


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    博客文章标签视图集

    list:
    返回博客文章标签列表
    """

    serializer_class = TagSerializer
    # 关闭分页
    pagination_class = None

    def get_queryset(self):
        return Tag.objects.all().order_by("name")

# 对搜索接口视图集的限流类进行单独设置5次/min
class PostSearchAnonRateThrottle(AnonRateThrottle):
    THROTTLE_RATES = {"anon": "5/min"}

class PostSearchView(HaystackViewSet):
    """
    搜索视图集

    list:
    返回搜索结果列表
    """

    index_models = [Post]
    serializer_class = PostHaystackSerializer
    throttle_classes = [PostSearchAnonRateThrottle]