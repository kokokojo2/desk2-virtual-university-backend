from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def get_regex_validator(field_name, custom_pattern=None, capitalized=True, hyphen=True, whitespace=True, numbers=True,
                        special=True):
    """
    Just a shortcut function to create a RegexValidator object with a default pattern and message template.
    :param special: bool - indicates whether special chars are included in the validation pattern
    :param numbers: bool - indicates whether numbers are included in the validation pattern
    :param custom_pattern: if custom pattern is specified, just passes it to a RegexValidator
    :param whitespace: bool - indicates whether whitespaces are included in the validation pattern
    :param hyphen: bool - indicates whether hyphens are included in the validation pattern
    :param capitalized: bool - indicates whether the text should be capitalized to pass a validation
    :param field_name: validation field name to fit a message template
    :returns: an instance of RegexValidator
    """

    pattern = r'[' + ('A-ZА-ЯІЇЄҐ' if capitalized else '') + (r'\d' if numbers else '') +\
              (r'!\.\(\).:,\;' if special else '') + ']' + '[a-zа-яіїєґA-ZА-ЯІЇЄҐ\'' + (r'\-' if hyphen else '') +\
              (r'\s' if whitespace else '') + (r'\d' if numbers else '') + (r'!\.\(\).,:;' if special else '') + ']+$'

    if custom_pattern:
        pattern = custom_pattern

    return RegexValidator(
        regex=pattern,
        message=f'Please enter a valid {field_name}.'
    )


def validate_number_len(value, digits_number):
    if digits_number != len(str(value)):
        raise ValidationError(f'Number of digits should equal to {digits_number}.')
