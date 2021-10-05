from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class ColorTagValidator(validators.RegexValidator):
    regex = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
    message = _('Enter color in HEX-code format')
