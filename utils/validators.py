from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def get_regex_validator(field_name, capitalized=True, hyphen=True, whitespace=True):
    """
    Just a shortcut function to create a RegexValidator object with a default pattern and message template.
    :param whitespace: bool - indicates whether whitespaces include in the validation pattern
    :param hyphen: bool - indicates whether hyphens include in the validation pattern
    :param capitalized: bool - indicates whether the text should be capitalized to pass a validation
    :param field_name: validation field name to fit a message template
    :returns: an instance of RegexValidator
    """
    pattern = (r'[A-ZА-Я]' if capitalized else '') + '[a-zа-я' + (r'\-' if hyphen else '') +\
              (r'\s' if whitespace else '') + ']+$'
    print(pattern)
    return RegexValidator(
        regex=pattern,
        message=f'Please enter a valid {field_name}.'
    )


def validate_number_len(value, digits_number):
    if digits_number != len(str(value)):
        raise ValidationError(f'Number of digits should equal to {digits_number}.')
