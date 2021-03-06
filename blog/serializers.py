from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Category, Tag
from drf_haystack.serializers import HaystackSerializerMixin
from rest_framework.fields import CharField

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
        ]

class PostListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    author = UserSerializer()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'created_time',
            'excerpt',
            'category',
            'author',
            'views',
        ]

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
        ]


class PostRetrieveSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    author = UserSerializer()
    tags = TagSerializer(many=True)
    toc = serializers.CharField()
    body_html = serializers.CharField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "created_time",
            "modified_time",
            "excerpt",
            "views",
            "category",
            "author",
            "tags",
            "toc",
            "body_html",
        ]

class HighlightedCharField(CharField):
    def to_representation(self, value):
        value = super().to_representation(value)
        request = self.context["request"]
        query = request.query_params["text"]
        highlighter = Highlighter(query)
        return highlighter.highlight(value)

class PostHaystackSerializer(HaystackSerializerMixin, PostListSerializer):
    title = HighlightedCharField(
        label="??????", help_text="????????????????????????????????? HTML ??????????????????????????? class???????????????????????????????????????????????????"
    )
    summary = HighlightedCharField(
        source="body",
        label="??????",
        help_text="????????????????????????????????? HTML ??????????????????????????? class???????????????????????????????????????????????????",
    )

    class Meta(PostListSerializer.Meta):
        search_fields = ["text"]
        fields = [
            "id",
            "title",
            "summary",
            "created_time",
            "excerpt",
            "category",
            "author",
            "views",
        ]