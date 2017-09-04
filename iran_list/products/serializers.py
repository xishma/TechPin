import traceback

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import raise_errors_on_nested_writes

from iran_list.products.models import Product, Type, Category, Version, Comment, Investment


class VersionSerializer(serializers.ModelSerializer):
    summary = serializers.ReadOnlyField(source='product_summary')

    class Meta:
        model = Version
        exclude = ['id', 'status', 'version_code', 'created_at', 'updated_at', 'product', 'editor', 'responder',
                   'summary']


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


class AddInvestmentSerializer(serializers.ModelSerializer):
    invested_on = serializers.SlugRelatedField(slug_field='slug', queryset=Product.objects.all(),
                                               help_text=_("Product slug"))
    investor = serializers.SlugRelatedField(slug_field='slug', queryset=Product.objects.all(),
                                            help_text=_("Product slug"))

    class Meta:
        model = Investment
        exclude = ['id', 'status', 'updated_at', 'created_at', 'user']

    def validate_year(self, year):
        if year < 1900 or year > 2100:
            raise serializers.ValidationError(_("Invalid amount for year!"))
        return year

    def validate_month(self, month):
        if month and (month < 1 or month > 12):
            raise serializers.ValidationError(_("Invalid amount for month!"))
        return month

    def create(self, validated_data):
        raise_errors_on_nested_writes('create', self, validated_data)
        validated_data['user'] = self.user
        try:
            instance = Investment.objects.create(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                'Got a `TypeError` when calling `%s.objects.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.objects.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception was:\n %s' %
                (
                    Investment.__name__,
                    Investment.__name__,
                    self.__class__.__name__,
                    tb
                )
            )
            raise TypeError(msg)

        return instance


class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name_en', 'slug', 'website']


class InvestmentSerializer(serializers.ModelSerializer):
    invested_on = ProductShortSerializer(read_only=True)
    investor = ProductShortSerializer(read_only=True)

    class Meta:
        model = Investment
        exclude = ['id', 'status', 'updated_at', 'created_at', 'user']


class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(many=True, slug_field='slug', read_only=True)
    product_type = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    details = VersionSerializer(read_only=True, source='version')
    rate_count = serializers.ReadOnlyField(source='p_rate_count')
    investments_received = InvestmentSerializer(read_only=True, many=True, source='get_investments_received')
    investments_done = InvestmentSerializer(read_only=True, many=True, source='get_investments_done')

    class Meta:
        model = Product
        exclude = ['status', 'hits', 'created_at', 'updated_at', 'creator', 'version', 'id']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
