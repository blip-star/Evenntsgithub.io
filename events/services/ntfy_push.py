def ntfy_status():
    from django.conf import settings
    return {
        'configured': bool(getattr(settings, 'NTFY_TOPIC', None)),
        'topic': getattr(settings, 'NTFY_TOPIC', ''),
    }
