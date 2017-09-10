from django.conf.urls import url
from rest_framework.schemas import get_schema_view

from . import views

schema_view = get_schema_view(title="Techpin Version 2")

urlpatterns = [
    url(r'^products/top/$', views.TopProductsView.as_view()),
    url(r'^products/all/$', views.ProductsView.as_view()),

    url(r'^auth/signup/$', views.SignupView.as_view()),
    url(r'^auth/user/(?P<pk>[0-9]+)/edit/$', views.EditUserView.as_view()),
    url(r'^auth/current-user/$', views.GetCurrentUserView.as_view()),
    url(r'^auth/login/$', views.LoginView.as_view()),
    url(r'^auth/google-login/$', views.GoogleLoginView.as_view()),
    url(r'^auth/change-password/$', views.ChangePasswordView.as_view()),
    url(r'^auth/password-reset/request/$', views.PasswordResetRequestView.as_view()),
    url(r'^auth/password-reset/confirm/$', views.PasswordResetConfirmView.as_view()),

    url(r'^$', schema_view)
]
