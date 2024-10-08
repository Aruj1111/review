import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_disposable_email(value):
    # This is a basic list of disposable email domains. You may want to expand this list.
    disposable_domains = [
        'temp-mail.org', 'tempmail.com', 'guerrillamail.com', '10minutemail.com',
        'mailinator.com', 'throwawaymail.com', 'yopmail.com', 'getairmail.com',
        'fakeinbox.com', 'sharklasers.com', 'guerrillamailblock.com', 'guerrillamail.net',
        'guerrillamail.org', 'guerrillamail.biz', 'spam4.me', 'grr.la', 'guerrillamail.de'
    ]
    
    domain = value.split('@')[-1].lower()
    if domain in disposable_domains:
        raise ValidationError(
            _('%(value)s is a disposable email address.'),
            params={'value': value},
        )