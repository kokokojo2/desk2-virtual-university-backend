from itertools import chain
from rest_framework.serializers import ModelSerializer


class NormalizedModelSerializer(ModelSerializer):
    """
    The generic serializer class that extends `ModelSerializer` and provides functionality to normalize model fields.
    **settings:**
        * `normalize_for_type` - dict that expects entries in format type:normalizer_callable.
        Every field of type that is specified in normalize_for_type dict will be normalizer used normalizer_callable.

        * `normalize_for_field` -  dict that expects entries in format field_name:normalizer_callable.
        Every field that is specified in normalize_for_field dict will be normalizer used normalizer_callable.

        The normalization is done before model validation (before `is_valid` method of `ModelSerializer` is called).

    """
    class Meta:
        normalize_for_type = {}
        normalize_for_field = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        rules_for_type = getattr(self.Meta, 'normalize_for_type', {})
        rules_for_field = getattr(self.Meta, 'normalize_for_field', {})
        print(rules_for_type, rules_for_field)

        for key, func in chain(rules_for_field.items(), rules_for_type.items()):
            if not callable(func):
                raise AttributeError(f'The normalize_for_type and normalize_for_field dicts of '
                                     f'NormalizedModelSerializer expects all values to be callable. However, '
                                     f'the value of type {func.__class__.__name__} was provided for key {key}.')

    def is_valid(self, raise_exception=False):
        rules_for_type = getattr(self.Meta, 'normalize_for_type', {})
        rules_for_field = getattr(self.Meta, 'normalize_for_field', {})

        if rules_for_type or rules_for_field:
            for name, value in self.initial_data.items():
                normalizer_for_type = rules_for_type.get(value.__class__, None)
                if normalizer_for_type:
                    value = normalizer_for_type(value)

                normalizer_for_field = rules_for_field.get(name, None)
                if normalizer_for_field:
                    value = normalizer_for_field(value)

                self.initial_data[name] = value

        return super().is_valid(raise_exception=raise_exception)
