def is_whatsapp_ready():
    from django.conf import settings
    return bool(settings.CALLMEBOT_API_KEY) if hasattr(settings, 'CALLMEBOT_API_KEY') else False
