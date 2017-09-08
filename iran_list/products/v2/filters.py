SEARCH_FIELDS = {
    'products': ['name_en', 'website'],
}

FILTER_FIELDS = {
    'products': {'type': 'product_type__slug__iexact', 'category': 'categories__slug__iexact',
                 'city': 'version__city__icontains', 'employees': 'version__employees_count'},
}

import re

from django.db.models import Q

from .constants import STOP_WORDS_RE


def normalize_query(query_string):
    """
    Split the query string into individual keywords, getting rid of unecessary
    spaces and grouping quoted words together.
    """
    find_terms = re.compile(r'"([^"]+)"|(\S+)').findall
    normalize_space = re.compile(r'\s{2,}').sub

    # Split the string into terms.
    terms = find_terms(query_string)

    # Only send unquoted terms through the stop words filter.
    for index, term in enumerate(terms):
        if term[1] is not '':
            # If the term is a stop word, delete it from the list.
            if STOP_WORDS_RE.sub('', term[1]) is '':
                del terms[index]

    return [normalize_space(' ', (t[0] or t[1]).strip()) for t in terms]


def get_query(query_string, search_fields):
    """Return a query which is a combination of Q objects."""
    query = None
    terms = normalize_query(query_string)

    for term in terms:
        or_query = None

        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q

        if query is None:
            query = or_query
        else:
            query = query & or_query

    return query


def filter_query(queryset, params, filters):
    kwargs = {}
    for filter_key in filters:
        if filter_key in params and params[filter_key] != 'all':
            kwargs[filters[filter_key]] = params[filter_key]
    return queryset.filter(**kwargs)
