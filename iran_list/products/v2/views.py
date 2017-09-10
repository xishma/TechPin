from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from iran_list.products.models import Product, PasswordResetTokenGenerator
from iran_list.products.v2 import utils
from iran_list.products.v2.filters import get_query, SEARCH_FIELDS, FILTER_FIELDS, filter_query
from iran_list.products.v2.response import ApiResponse
from iran_list.settings import GOOGLE_OAUTH2_CLIENT_ID
from .base_views import ListView, RetrieveView, CreateView, UpdateView
from .serializers import ProductSerializer, UserSerializer, SignupSerializer, LoginSerializer, GoogleLoginSerializer, \
    ChangePasswordSerializer, EditUserSerializer, EmailPasswordResetSerializer, EmailPasswordResetConfirmSerializer


class TopProductsView(ListView):
    """
    Shows a list of top products, in the following categories:
    100m: Worth than 100 million dollars
    10m: Worth than 10 million dollars
    1m: Worth than 1 million dollars
    new: Top new products
    """
    permission_classes = []
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(status='pub')
    model_name = 'product'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        products_100m_queryset = queryset.filter(categories__slug='100m').order_by("-ranking")
        products_100m = self.get_serializer(products_100m_queryset, many=True)
        products_100m_count = products_100m_queryset.count()

        products_10m_queryset = queryset.filter(categories__slug='10m').order_by("-ranking")[:25 - products_100m_count]
        products_10m = self.get_serializer(products_10m_queryset, many=True)

        products_1m_queryset = queryset.filter(categories__slug='1m').order_by("-ranking")[:25]
        products_1m = self.get_serializer(products_1m_queryset, many=True)

        new_products = self.get_serializer(queryset.order_by("-created_at")[:25], many=True)

        products = {
            '100m': products_100m.data,
            '10m': products_10m.data,
            '1m': products_1m.data,
            'new': new_products.data,
        }
        response_data = ApiResponse.get_base_response(data={'%ss' % self.model_name: products},
                                                      message=self.message['list'])

        return Response(response_data)


class ProductsView(ListView):
    """
    Give a list of all products, with ability to search and filter.
    Parameters: search (for searching). type, category, city, employees (e.g. 5-10), for filtering. grouped (Group by first letter of the name).
    """
    permission_classes = []
    serializer_class = ProductSerializer
    model_name = 'product'

    def get_queryset(self):
        queryset = Product.objects.filter(status='pub')

        search_query = self.request.query_params.get('search')
        if search_query:
            entry_query = get_query(search_query, SEARCH_FIELDS['products'])
            queryset = queryset.filter(entry_query)

        queryset = filter_query(queryset, self.request.query_params, FILTER_FIELDS['products'])

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        products = {
        }

        if self.request.query_params.get('grouped', None):
            for product in queryset:
                if product.name_en[0] in [str(a) for a in range(0, 10)]:
                    if "#" in products:
                        products["#"].append(ProductSerializer(product).data)
                    else:
                        products["#"] = [ProductSerializer(product).data]
                else:
                    if product.name_en[0].upper() in products:
                        products[product.name_en[0].upper()].append(ProductSerializer(product).data)
                    else:
                        products[product.name_en[0].upper()] = [ProductSerializer(product).data]

        else:
            products = ProductSerializer(queryset, many=True).data

        response_data = ApiResponse.get_base_response(data={'%ss' % self.model_name: products},
                                                      message=self.message['list'])
        return Response(response_data)


class SignupView(CreateView):
    """
    post:
    Signs up a user in system.
    """
    permission_classes = []
    serializer_class = SignupSerializer
    model_name = 'user'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        data = {self.model_name: serializer.data, 'gp_client_id': GOOGLE_OAUTH2_CLIENT_ID}

        return Response(ApiResponse.get_base_response(response_code=status.HTTP_201_CREATED, data=data,
                                                      message=self.message['create']),
                        status=status.HTTP_201_CREATED, headers=headers)


class EditUserView(UpdateView):
    """
    put:
    Updates the user information.
    patch:
    Updates the user information.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EditUserSerializer
    model_name = 'user'

    def get_queryset(self):
        return User.objects.get(id=self.request.user.id)


class LoginView(CreateView):
    """
    Use this endpoint to obtain user auth token
    """
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response_data = {'user': UserSerializer(serializer.user).data,
                             'token': serializer.token,
                             'gp_client_id': GOOGLE_OAUTH2_CLIENT_ID}
            response = ApiResponse.get_base_response(data=response_data)
        else:
            # This part will never happen, because if the're any error in the validation, it'll raise an exception
            response = ApiResponse.get_fail_response()
        return Response(response)


class GoogleLoginView(CreateView):
    """
    Use this endpoint for login with google action
    """
    serializer_class = GoogleLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response_data = {'user': UserSerializer(serializer.user).data,
                             'token': serializer.token,
                             'gp_client_id': GOOGLE_OAUTH2_CLIENT_ID}
            response = ApiResponse.get_base_response(data=response_data)
        else:
            # This part will never happen, because if the're any error in the validation, it'll raise an exception
            response = ApiResponse.get_fail_response()
        return Response(response)


class ChangePasswordView(CreateView):
    """
    Use this endpoint to change user password
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.set_user(request.user)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_data = {'message': _("Password was changed successfully!"), 'user': UserSerializer(request.user).data}
        return Response(ApiResponse.get_base_response(HTTP_200_OK, data=response_data))


class PasswordResetRequestView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to send email to user with password reset link.
    """
    serializer_class = EmailPasswordResetSerializer
    permission_classes = []

    _users = None

    def _action(self, serializer):
        _user = self.get_user(serializer.data['email'])

        if not _user:
            return Response(
                ApiResponse.get_fail_response(general_errors=_("Email not found in system.")))
        web_token = self.send_password_reset_email(_user)
        return Response(
            ApiResponse.get_base_response(data={'email': _user.email, 'token': web_token},
                                          message=_("We sent a code to your email. Use it for password reset")))

    def get_user(self, email):
        try:
            _user = User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist:
            return None
        return _user

    def send_password_reset_email(self, user):
        token = PasswordResetTokenGenerator().make_token(user)
        email_token, web_token = token.split(',')
        email_factory = utils.UserPasswordResetEmailFactory.from_request(self.request, token=email_token, user=user)
        email = email_factory.create()
        email.send()
        return web_token


class PasswordResetConfirmView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to finish email reset password process.
    """
    permission_classes = []
    token_generator = PasswordResetTokenGenerator()

    def get_serializer_class(self):
        return EmailPasswordResetConfirmSerializer

    def _action(self, serializer):
        serializer.user.set_password(serializer.data['new_password'])
        serializer.user.save()
        return Response(ApiResponse.get_base_response(message=_("Password was reset successfully.")))


class GetCurrentUserView(RetrieveView):
    """
    Gives the basic info of the current user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.get_serializer(instance)
        return Response(
            ApiResponse.get_base_response(data={'user': serializer.data}))
