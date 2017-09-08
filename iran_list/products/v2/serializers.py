from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes

from iran_list.products.models import Product, Type, Category, Version, Comment, Investment, DueDiligenceMessage


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        exclude = []


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = []


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


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
        if self.user and self.user.id:
            validated_data['user'] = self.user

        return super(AddInvestmentSerializer, self).create(validated_data)


class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name_en', 'slug', 'website']


class VersionSerializer(serializers.ModelSerializer):
    summary = serializers.ReadOnlyField(source='product_summary')
    created_at = serializers.ReadOnlyField()
    version_code = serializers.ReadOnlyField()
    product = ProductShortSerializer(read_only=True)

    class Meta:
        model = Version
        exclude = ['id', 'status', 'version_code', 'created_at', 'updated_at', 'product', 'editor', 'responder',
                   'summary']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductShortSerializer(read_only=True)

    class Meta:
        model = Comment
        exclude = ['id', 'status', 'updated_at', 'product']


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


class DueDiligenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DueDiligenceMessage
        fields = ('name', 'email', 'phone_number', 'company_description')
