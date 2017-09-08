from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from oauth2client import client, crypt
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.serializers import raise_errors_on_nested_writes

from iran_list.products.models import Product, Type, Category, Version, Comment, Investment, DueDiligenceMessage, \
    Profile, SocialLogin
from iran_list.settings import GOOGLE_OAUTH2_CLIENT_ID


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        exclude = []


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = []


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'email', 'password')

    def validate_password(self, password):
        errors = validate_password(password=password)
        if errors:
            raise serializers.ValidationError(errors)
        return password

    def validate_email(self, email):
        if User.objects.filter(email=email).count() > 0:
            raise serializers.ValidationError(_("Email is already in use!"))
        return email

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['username'] = validated_data['email'].lower()

        user = super().create(validated_data)
        user.set_password(password)
        user.save()

        profile = Profile(user=user)
        profile.save()

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            try:
                user = User.objects.get(Q(email=username) | Q(username=username))
            except User.DoesNotExist:
                user = None
            if user:
                user = authenticate(username=user.username, password=password)
            if user:
                # Create a profile for user, if they don't have one
                Profile.objects.get_or_create(user=user)
                token = Token.objects.get_or_create(user=user)[0]
                self.user = user
                self.token = token.key
            else:
                raise serializers.ValidationError(_('Unable to log in with provided credentials.'))
        else:
            raise serializers.ValidationError(_('Must include "username" and "password".'))

        return attrs


class GoogleLoginSerializer(serializers.Serializer):
    idtoken = serializers.CharField(required=True)

    def validate(self, attrs):
        token = attrs.get('idtoken')
        try:
            idinfo = client.verify_id_token(token, GOOGLE_OAUTH2_CLIENT_ID)

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise serializers.ValidationError(_("Wrong token issuer!"))

        except crypt.AppIdentityError:
            # Invalid token
            raise serializers.ValidationError(_("Invalid token!"))

        userid = idinfo['sub']

        social_user = None

        try:
            social_user = SocialLogin.objects.get(social_unique_id=userid)
        except SocialLogin.DoesNotExist:
            user = User(first_name=idinfo['given_name'], last_name=idinfo['family_name'], email=idinfo['email'],
                        username=idinfo['email'], password=User.objects.make_random_password())
            user.save()

            try:
                social_user = SocialLogin(user=user, social_unique_id=userid)
                social_user.save()
            except:
                # If can't create a social user entry for any reason, delete the created user.
                user.delete()

        if social_user is not None:
            user = User.objects.get(id=social_user.user_id)
            if user is not None:
                token = Token.objects.get_or_create(user=user)[0]
                self.user = user
                self.token = token.key
            else:
                social_user.delete()
                raise serializers.ValidationError(_("Failed to login!"))
        else:
            raise serializers.ValidationError(_("Failed to login!"))

        return attrs


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
