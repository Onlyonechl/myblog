import markdown, re
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Tag
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.views.generic import ListView, DetailView
from pure_pagination.mixins import PaginationMixin
from django.contrib import messages
from django.db.models import Q

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