from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'), #在 URL 配置中把 index 视图替换成类视图 IndexView
    # 对 url 函数来说，第二个参数传入的值必须是一个函数。而 IndexView 是一个类，不能直接替代 index 函数。好在将类视图转换成函数视图非常简单，只需调用类视图的 as_view() 方法即可
    # path('post/<int:pk>/', views.detail, name='detail'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    path('archives/<int:year>/<int:month>/', views.archive, name='archive'),
    # path('categories/<int:pk>/', views.category, name='category'),
    path('categories/<int:pk>/', views.CategoryView.as_view(), name='category'), #在 URL 配置中把 category 视图替换成类视图 CategoryView
    path('tags/<int:pk>/', views.tag, name='tag'),
    path('categories', views.categories, name='categories'),
    # path('search/', views.search, name='search'),
    # path('api/index/', views.index),
    #path('api/index/', views.IndexPostListAPIView.as_view()),
    path("api/index/", views.index),
]