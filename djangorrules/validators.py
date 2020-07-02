from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_nonzero(value):
    if value == 0:
        raise ValidationError(
            _('Quantity %(value)s is not allowed'),
            params={'value': value},
        )
