from django.db.models import Q

def filter_params_from_request(request):
    return {
        'q': request.GET.get('q', ''),
        'source': request.GET.get('source', ''),
        'county': request.GET.get('county', ''),
        'category': request.GET.get('category', ''),
        'recommended': request.GET.get('recommended', ''),
    }

def apply_event_filters(queryset, params):
    if params.get('q'):
        queryset = queryset.filter(Q(title__icontains=params['q']) | Q(venue__icontains=params['q']))
    if params.get('source'):
        queryset = queryset.filter(source=params['source'])
    if params.get('county'):
        queryset = queryset.filter(county__icontains=params['county'])
    if params.get('category') and hasattr(queryset.model, 'ai_category'):
        queryset = queryset.filter(ai_category=params['category'])
    if params.get('recommended') == '1':
        queryset = queryset.filter(is_recommended=True)
    return queryset

def build_query_string(params):
    return '&'.join([f'{k}={v}' for k, v in params.items() if v])
