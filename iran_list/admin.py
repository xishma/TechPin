from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from iran_list.products.models import Product, Version, Investment, DueDiligenceMessage

admin_site = admin.site
admin_site.index_template = "admin/custom_index.html"


@staff_member_required
@never_cache
def admin_index(request, extra_context=None):
    """
    Displays the main admin index page, which lists all of the installed
    apps that have been registered in this site.
    """
    app_list = admin_site.get_app_list(request)

    context = dict(
        admin_site.each_context(request),
        title=admin_site.index_title,
        app_list=app_list,
    )

    products = Product.objects.filter(status='pen').order_by('-id')[0:10]
    versions = Version.objects.filter(status='pen').order_by('-id')[0:10]
    investments = Investment.objects.filter(status='pen').order_by('-id')[0:10]
    messages = DueDiligenceMessage.objects.filter(status='new').order_by('-id')[0:10]

    context['activity_tables'] = [
        {'title': Product._meta.verbose_name.title(), 'data': products},
        {'title': Version._meta.verbose_name.title(), 'data': versions},
        {'title': Investment._meta.verbose_name.title(), 'data': investments},
        {'title': DueDiligenceMessage._meta.verbose_name.title(), 'data': messages}]
    context.update(extra_context or {})
    request.current_app = admin_site.name
    return TemplateResponse(request, admin_site.index_template or 'admin/index.html', context)
