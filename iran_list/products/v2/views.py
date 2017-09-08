from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from iran_list.products.models import Product
from iran_list.products.v2.filters import get_query, SEARCH_FIELDS, FILTER_FIELDS, filter_query
from iran_list.products.v2.response import ApiResponse
from iran_list.settings import GOOGLE_OAUTH2_CLIENT_ID
from .base_views import ListView, RetrieveView, CreateView
from .serializers import ProductSerializer, UserSerializer, SignupSerializer, LoginSerializer, GoogleLoginSerializer


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


class TraineeSignupView(CreateView):
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
