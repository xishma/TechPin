from django.conf.urls import url
from rest_framework.schemas import get_schema_view

from . import views

schema_view = get_schema_view(title="Techpin Version 2")

urlpatterns = [
    url(r'^products/top/?$', views.TopProductsView.as_view()),
    url(r'^products/all/?$', views.ProductsView.as_view()),
    url(r'^$', schema_view)
]
