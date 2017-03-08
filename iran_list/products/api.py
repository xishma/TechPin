from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from oauth2client import client, crypt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view

from iran_list.products.forms import SignupForm, LoginForm, ChangePasswordForm, EditUserForm, ResetPasswordForm, \
    ProductForm, VersionForm, CommentForm, RateForm
from iran_list.products.models import ResetPasswordCode, Profile, Product, get_sentinel_user, Version, Comment, Rate, \
    Type, Category
from iran_list.products.models import SocialLogin
from iran_list.products.serializers import ProductSerializer, JSONResponse, TypeSerializer, CategorySerializer, \
    VersionSerializer, CommentSerializer
from iran_list.settings import SITE_ADDRESS


def pack_data(request, data):
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        user_data = {'username': user.username, 'first_name': user.first_name,
                     'last_name': user.last_name, 'email': user.email}

        data['user'] = user_data
    else:
        data['user'] = None
    data['site_address'] = SITE_ADDRESS

    return data


@api_view(['GET'])
def home(request):
    products = Product.objects.filter(status="pub")

    type_object = None
    if 'type' in request.GET:
        type_slug = request.GET['type']
        type_object = get_object_or_404(Type, slug=type_slug)
        products = products.filter(product_type=type_object)

    category_object = None
    if 'category' in request.GET:
        category_slug = request.GET['category']
        category_object = get_object_or_404(Category, slug=category_slug)
        products = products.filter(categories=category_object)

    # top_p_products = products.annotate(rate_count=Count('rates')).order_by("-rate_count")[:25]
    # top_p_serializer = ProductSerializer(top_p_products, many=True)

    top_new_products = products.order_by("-created_at")[:25]
    top_new_serializer = ProductSerializer(top_new_products, many=True)

    top_ranked = products.order_by("-ranking")[:25]
    top_ranked_serializer = ProductSerializer(top_ranked, many=True)

    top_rank_ids = [product.id for product in top_ranked]
    top_new_ids = [product.id for product in top_new_products]
    top_e_products = products.exclude(id__in=top_new_ids).exclude(id__in=top_rank_ids).order_by("-hits")[:25]
    top_e_serializer = ProductSerializer(top_e_products, many=True)

    data = {'random_products': top_e_serializer.data,
            'top_new_serializer': top_new_serializer.data,
            'top_ranked_serializer': top_ranked_serializer.data}

    if type_object:
        type_serializer = TypeSerializer(type_object)
        data['type'] = type_serializer.data

    if category_object:
        category_serializer = CategorySerializer(category_object)
        data['category'] = category_serializer.data

    data = pack_data(request, data)

    return JSONResponse(data)


@api_view(['GET'])
def all_products(request):
    products = Product.objects.filter(status="pub").order_by("name_en")
    products_dict = {}

    for product in products:
        if product.name_en[0] in [str(a) for a in range(0, 10)]:
            if "#" in products_dict:
                products_dict["#"].append(ProductSerializer(product).data)
            else:
                products_dict["#"] = [ProductSerializer(product).data]
        else:
            if product.name_en[0].upper() in products_dict:
                products_dict[product.name_en[0].upper()].append(ProductSerializer(product).data)
            else:
                products_dict[product.name_en[0].upper()] = [ProductSerializer(product).data]

    data = pack_data(request, {'products': products_dict})

    return JSONResponse(data)


# @api_view(['POST'])
@csrf_exempt
def signup(request):
    """
    :param request: first_name, email, password, confirm_password
    :return: success, datails
    """
    if request.method != "POST":
        return JSONResponse({'success': False, 'response': 405, 'detail': 'Invalid method!'})
    elif request.user.is_authenticated():
        return JSONResponse({'success': False, 'response': 403, 'detail': 'Already logged in!'})
    else:
        signup_form = SignupForm(request.data)

        if signup_form.is_valid():
            user = signup_form.save()
            if user:
                data = {'success': True}
            else:
                return JSONResponse(
                    {'success': False, 'response': 500, 'detail': _("Unknown errors during signup. Please try again.")})
        else:
            data = {'success': False, 'response': 555, 'detail': dict(signup_form.errors.items())}

    data['gp_client_id'] = settings.GOOGLE_OAUTH2_C2LIENT_ID
    data = pack_data(request, data)
    return JSONResponse(data)


# @api_view(['POST'])
@csrf_exempt
def signin(request):
    """
        :param request: email, password
        :return: success, datails
    """
    if request.method != "POST":
        return JSONResponse({'success': False, 'response': 405, 'detail': 'Invalid method!'})
    elif request.user.is_authenticated():
        return JSONResponse({'success': False, 'response': 403, 'detail': 'Already logged in!'})
    else:
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            user = login_form.user
            if user is not None:
                login(request, user)
                if Profile.objects.filter(user_id=user.id).count() == 0:
                    Profile.objects.create(user=user)
                token = Token.objects.get_or_create(user=user)[0]
                data = {'success': True, 'api-token': token.key}
            else:
                return JSONResponse({'success': False, 'response': 500, 'detail': 'Failed to login. Please try again!'})
        else:
            data = {'success': False, 'response': 555, 'detail': dict(login_form.errors.items())}

    data['gp_client_id'] = settings.GOOGLE_OAUTH2_CLIENT_ID
    data = pack_data(request, data)
    return JSONResponse(data)


@csrf_exempt
def google_signin(request):
    if request.method != "POST":
        data = {'success': False, 'response': 405, 'detail': 'Invalid method!'}
    elif request.user.is_authenticated():
        data = {'success': False, 'response': 403, 'detail': 'Already logged in!'}

    else:
        # (Receive token by HTTPS POST)
        token = request.POST.get("idtoken", "")
        data = {'success': True, 'user': True, 'token': token}

        try:
            idinfo = client.verify_id_token(token, settings.GOOGLE_OAUTH2_CLIENT_ID)

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise crypt.AppIdentityError("Wrong issuer.")
                # If auth request is from a G Suite domain:
                # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
                #    raise crypt.AppIdentityError("Wrong hosted domain.")

        except crypt.AppIdentityError:
            # Invalid token
            return JSONResponse({'success': False, 'response': 500})

        userid = idinfo['sub']

        social_user = None
        # check if user is not in the social login table then create it, else just log him in
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
                user.delete()

        if social_user is not None:
            user = User.objects.get(id=social_user.user_id)
            if user is not None:
                login(request, user)
                token = Token.objects.get_or_create(user=user)[0]
                data['api-token'] = token.key
            else:
                social_user.delete()
                return JSONResponse({'success': False, 'response': 500, })
        else:
            return JSONResponse({'success': False, 'response': 500, })

    data = pack_data(request, data)
    return JSONResponse(data)


@csrf_exempt
def change_password(request):
    if request.method != "POST":
        return JSONResponse({'success': False, 'response': 405, 'detail': 'Invalid method!'})
    elif not request.user.is_authenticated():
        return JSONResponse({'success': False, 'response': 403, 'detail': 'Login required!'})
    else:
        password_form = ChangePasswordForm(request.user, data=request.POST)

        if password_form.is_valid():
            if password_form.save():
                data = {'success': True, 'detail': _(u'Password Successfully changed!')}
            else:
                return JSONResponse({'success': False, 'detail': _('Failed to change password. Please try again!')})
        else:
            return JSONResponse({'success': False, 'detail': dict(password_form.errors.items())})

    data = pack_data(request, data)
    return JSONResponse(data)


@csrf_exempt
def edit_profile(request):
    if request.method != "POST":
        return JSONResponse({'success': False, 'response': 405, 'detail': 'Invalid method!'})
    elif not request.user.is_authenticated():
        return JSONResponse({'success': False, 'response': 403, 'detail': 'Login required!'})
    else:
        user = request.user
        user_form = EditUserForm(request.POST, instance=user)

        if user_form.is_valid():
            user_form.save()
            data = {'success': True}
        else:
            return JSONResponse({'success': False, 'response': 555, 'detail': dict(user_form.errors.items())})

    data = pack_data(request, data)
    return JSONResponse(data)


@csrf_exempt
def request_reset(request):
    if request.method != "POST":
        return JSONResponse({'success': False, 'response': 405, 'detail': 'Invalid method!'})
    else:
        form = ResetPasswordForm(request.POST)

        if form.is_valid():
            sent = form.save()
            if not sent:
                return JSONResponse(
                    {'success': False, 'response': 500, 'detail': 'Whoops! Something went wrong! Please Try again.'})
            else:
                data = {'success': True, 'detail': _(u'We Sent You an Email for Password Reset.')}
        else:
            return JSONResponse({'success': False, 'response': 555, 'detail': dict(form.errors.items())})

    data = pack_data(request, data)
    return render_to_response('users/forgot_password.html', data)


@csrf_exempt
def reset_pass(request, reset_code):
    if request.method != "POST":
        return JSONResponse({'success': False, 'response': 405, 'detail': 'Invalid method!'})
    else:
        try:
            reset_code = ResetPasswordCode.objects.get(code=reset_code)
        except ResetPasswordCode.DoesNotExist:
            return JSONResponse({'success': False, 'response': 404, 'detail': _(u'Invalid Link!')})

        user = reset_code.profile.user
        password_form = ChangePasswordForm(user, reset=True, data=request.POST)

        if password_form.is_valid():
            if password_form.save():
                reset_code.delete()
                data = {'success': True, 'detail': _(u'Password Successfully changed!')}
            else:
                return JSONResponse(
                    {'success': False, 'response': 500, 'detail': 'Failed to set password. Please try again!'})
        else:
            return JSONResponse({'success': False, 'response': 555, 'detail': dict(password_form.errors.items())})

    data = pack_data(request, data)
    return render_to_response('users/forgot_password.html', data)


@csrf_exempt
def signout(request):
    logout(request)
    return JSONResponse({'success': True})


@csrf_exempt
def add_product(request):
    if request.method != "POST":
        return JSONResponse({'success': False, 'response': 405, 'detail': 'Invalid method!'})
    else:
        product = Product()
        if request.user.is_authenticated:
            product.creator = Profile.get_user_profile(request.user)
        else:
            product.creator = Profile.get_user_profile(get_sentinel_user())

        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            if product:
                data = {'success': True}
            else:
                return JSONResponse(
                    {'success': False, 'response': 500, 'detail': 'Failed to set password. Please try again!'})
        else:
            return JSONResponse({'success': False, 'response': 555, 'detail': dict(form.errors.items())})

    data = pack_data(request, data)
    return JSONResponse(data)


@csrf_exempt
def add_version(request, product_slug):
    if request.method != "PATCH":
        return JSONResponse({'success': False, 'response': 405, 'detail': 'Invalid method!'})
    else:
        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            return JSONResponse({'success': False, 'response': 404, 'detail': 'Invalid product slug.'})

        if product.version is not None and not request.user.is_authenticated:
            return JSONResponse({'success': False, 'response': 403, 'detail': 'You should login first.'})

        version = Version()
        version.version_code = 0
        version.product = product
        if request.user.is_authenticated:
            version.editor = Profile.get_user_profile(request.user)
        else:
            version.editor = Profile.get_user_profile(get_sentinel_user())

        form = VersionForm(request.POST, request.FILES, instance=version)
        if form.is_valid():
            form.save()
            data = {'success': True, 'detail': _(u'Successfully added your update. We will review and apply it asap!')}
        else:
            return JSONResponse({'success': False, 'response': 555, 'detail': dict(form.errors.items())})

    data = pack_data(request, data)
    return JSONResponse(data)


def product_page(request, slug):
    if slug.endswith("/"):
        slug = slug[:-1]

    product = get_object_or_404(Product, slug=slug, status="pub")

    product.hit()

    rate = None
    if request.user.is_authenticated:
        user_profile = Profile.get_user_profile(request.user)
        try:
            rate = Rate.objects.get(user_id=user_profile.id, product_id=product.id, user_type=user_profile.is_editor)
        except Rate.DoesNotExist:
            pass
        except Rate.MultipleObjectsReturned:
            rates = Rate.objects.filter(user_id=user_profile.id, product_id=product.id,
                                        user_type=user_profile.is_editor)
            rate = rates[0]
            for i in range(1, rates.count()):
                _rate = rates[i]
                _rate.delete()

    comments = product.comments.filter(status="pub")

    product_data = ProductSerializer(product).data
    version_data = VersionSerializer(product.last_approved_version()).data
    comments_data = CommentSerializer(comments, many=True).data

    data = {'product': product_data, 'version': version_data, 'comments': comments_data, 'rate': None}

    if rate is not None:
        data['rate'] = rate.rate

    data = pack_data(request, data)
    return JSONResponse(data)


@csrf_exempt
def rate_product(request, product_slug):
    if request.method != "POST":
        return JSONResponse({'success': False, 'response': 405, 'detail': 'Invalid method!'})
    elif not request.user.is_authenticated():
        return JSONResponse({'success': False, 'response': 403, 'detail': 'Login required!'})
    else:
        if product_slug.endswith("/"):
            product_slug = product_slug[:-1]

        try:
            product = Product.objects.get(slug=product_slug, status="pub")
            user_profile = Profile.get_user_profile(request.user)
            try:
                rate = Rate.objects.get(user_id=user_profile.id, product_id=product.id,
                                        user_type=user_profile.is_editor)
            except Rate.MultipleObjectsReturned:
                rates = Rate.objects.filter(user_id=user_profile.id, product_id=product.id,
                                            user_type=user_profile.is_editor)
                rate = rates[0]
                for i in range(1, rates.count()):
                    _rate = rates[i]
                    _rate.delete()
            except Rate.DoesNotExist:
                rate = Rate()
                user_profile = Profile.get_user_profile(request.user)
                rate.user = user_profile
                rate.user_type = user_profile.is_editor
                rate.product = product

            rate_form = RateForm(request.POST, instance=rate)
            if rate_form.is_valid():
                rate_form.save()
                data = {'success': True}

            else:
                return JSONResponse({'success': False, 'response': 555, 'detail': dict(rate_form.errors.items())})

        except Product.DoesNotExist:
            return JSONResponse({'success': False, 'response': 404, 'detail': 'Invalid product slug!'})

    return JSONResponse(data)


@csrf_exempt
def review_product(request, product_slug):
    if request.method != "POST":
        return JSONResponse({'success': False, 'response': 405, 'detail': 'Invalid method!'})
    elif not request.user.is_authenticated():
        return JSONResponse({'success': False, 'response': 403, 'detail': 'Login required!'})
    else:
        if product_slug.endswith("/"):
            product_slug = product_slug[:-1]

        try:
            product = Product.objects.get(slug=product_slug, status="pub")

            comment = Comment()
            comment.user = Profile.get_user_profile(request.user)
            comment.product = product
            comment_form = CommentForm(request.POST, instance=comment)

            if comment_form.is_valid():
                comment_form.save()
                data = {'success': True}
            else:
                return JSONResponse({'success': False, 'response': 555, 'detail': dict(comment_form.errors.items())})

        except Product.DoesNotExist:
            return JSONResponse({'success': False, 'response': 404, 'detail': 'Invalid product slug!'})

    return JSONResponse(data)


def about(request):
    data = pack_data(request, {'page': 'about'})
    return JSONResponse(data)


def contribute(request):
    data = pack_data(request, {'page': 'contribute'})
    return JSONResponse(data)


def categories(request):
    category_list = Category.objects.all()
    category_serializer = CategorySerializer(category_list, many=True)
    data = pack_data(request, {'categories': category_serializer.data})
    return JSONResponse(data)
