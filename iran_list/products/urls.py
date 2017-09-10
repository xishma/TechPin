from django.conf.urls import url
from rest_framework.schemas import get_schema_view

from .views import signin, signup, signout, edit_profile, change_password, home, request_reset, reset_pass, add_product, \
    add_version, product_page, all_products, about, contribute, rate_product, google_signin, review_product, categories, \
    types, get_rating, category_products, random_product_page, AddInvestmentView, AddDueDiligenceView, ProductListView, \
    SiteInfoListView

schema_view = get_schema_view(title="Techpin")

urlpatterns = [
    url(r'^signup/?$', signup, name='api_signup'),
    url(r'^login/?$', signin, name='api_login'),
    url(r'^google-login/?$', google_signin, name='api_google_login'),
    url(r'^logout/?$', signout, name='api_logout'),

    url(r'^change-password/?$', change_password, name='api_change_password'),
    url(r'^edit-profile/?$', edit_profile, name='api_edit_profile'),

    url(r'^reset-password/([0-9a-f]+)/?$', reset_pass, name='api_reset_pass'),
    url(r'^forgot-password/?$', request_reset, name='api_forgot_pass'),

    url(r'^products/?$', all_products, name='api_all_products'),
    url(r'^products/top/?$', home, name='api_home'),
    url(r'^products/names/?$', ProductListView.as_view()),

    url(r'^category/(.+)/products/?$', category_products, name='category_products'),

    url(r'^products/add/?$', add_product, name='api_add_product'),
    url(r'^products/(.+)/versions/add/?$', add_version, name='api_add_version'),
    url(r'^products/(.+)/rate/?$', rate_product, name='api_rate_product'),
    url(r'^products/(.+)/comments/?$', review_product, name='api_rate_product'),
    url(r'^products/(.+)/?$', product_page, name='api_product_page'),
    url(r'^random-product/?$', random_product_page, name='api_random_product_page'),
    url(r'^rates/(.+)/?$', get_rating, name='api_get_rating'),

    url(r'^categories/?$', categories, name='api_categories'),
    url(r'^product_types/?$', types, name='api_types'),

    url(r'^investments/add/$', AddInvestmentView.as_view()),
    url(r'^due-diligence-message/add/$', AddDueDiligenceView.as_view()),

    url(r'^site-info/list/$', SiteInfoListView.as_view()),

    url(r'^about/?$', about, name='api_about'),
    url(r'^contribute/?$', contribute, name='api_contribute'),
    url(r'^$', schema_view)

]
