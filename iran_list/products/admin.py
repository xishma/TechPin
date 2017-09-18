from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from iran_list.products.models import Type, Category, Product, Profile, Version, Comment, Rate, Investment, \
    DueDiligenceMessage, SiteInfo


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = []


class ProductAdmin(admin.ModelAdmin):
    form = ProductForm

    list_display = ['name_en', 'status', 'created_at']
    list_filter = ('product_type', 'status', 'categories')
    filter_horizontal = ('categories',)
    readonly_fields = ['creator', 'created_at', 'updated_at', 'slug']
    search_fields = ['name_en', 'website']

    class Meta:
        exclude = []


class VersionForm(forms.ModelForm):
    class Meta:
        model = Version
        exclude = ["responder"]

    def clean(self):
        cleaned_data = super(VersionForm, self).clean()

        if not self.instance.can_respond():
            raise forms.ValidationError(_(u"Can't respond to this version. Check earlier versions."))


class VersionAdmin(admin.ModelAdmin):
    form = VersionForm

    list_display = ['__str__', 'version_code', 'status']
    list_filter = ('status',)
    readonly_fields = ['version_code', 'product', 'editor', 'created_at', 'updated_at']
    search_fields = ['product__name_en', 'product__website', 'email']

    class Meta:
        exclude = []


class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'status', 'is_acquired']
    list_filter = ['status', 'is_acquired']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['investor__name_en', 'investor__website', 'invested_on__name_en', 'invested_on__website']

    class Meta:
        exclude = []


class DueDiligenceMessageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'status']
    list_filter = ['status']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['name', 'phone_number', 'email', 'company_name']

    class Meta:
        exclude = []


class SiteInfoAdmin(admin.ModelAdmin):
    list_display = ['title', 'name']
    list_filter = []
    filter_horizontal = []
    readonly_fields = []
    search_fields = ['title', 'text', 'button_text', 'name']


admin.site.register(Type)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Investment, InvestmentAdmin)
admin.site.register(DueDiligenceMessage, DueDiligenceMessageAdmin)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Rate)
admin.site.register(SiteInfo, SiteInfoAdmin)
