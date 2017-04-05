from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from iran_list.products.models import Product, Type, Category, Version, Comment


class VersionSerializer(serializers.ModelSerializer):
    summary = serializers.ReadOnlyField(source='product_summary')

    class Meta:
        model = Version
        exclude = ['id', 'status', 'version_code', 'created_at', 'updated_at', 'product', 'editor', 'responder',
                   'summary']


class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(many=True, slug_field='slug', read_only=True)
    product_type = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    details = VersionSerializer(read_only=True,source='version')
    rate_count = serializers.ReadOnlyField(source='p_rate_count')

    class Meta:
        model = Product
        exclude = ['status', 'hits', 'created_at', 'updated_at', 'creator', 'version', 'id']


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        exclude = []


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = []


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Comment
        exclude = ['id', 'status', 'updated_at', 'product']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
