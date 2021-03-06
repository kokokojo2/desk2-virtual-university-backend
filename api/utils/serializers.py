from itertools import chain
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rules_for_type = getattr(self.Meta, 'normalize_for_type', {})
        rules_for_field = getattr(self.Meta, 'normalize_for_field', {})

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


class WriteOnCreationMixin:
    """
    Provides functionality that allows to specify a list of fields to be written only when creating an object.
    If serializer is used to update an existing object, the fields specified in **Meta.create_only_fields** will be not
    updated.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_only_fields = getattr(self.Meta, 'create_only_fields', [])

    def update(self, instance, validated_data):
        for key in self.create_only_fields:
            validated_data.pop(key, None)

        return super().update(instance, validated_data)


class PrimaryKeyWriteMixin:
    """
    Provides a primary key serialization when creating an instance. Intended to be used for nested serialization.
    Behaviour:
    Returns related object on deserialization.
    Returns a json representation of the related object on serialization.
    Note: the data of this serializer should be the primary key of the related object.
    To better understand the behaviour examine this question - https://stackoverflow.com/questions/28010663/serializerclass-field-on-serializer-save-from-primary-key
    """

    def _get_model_class(self):
        return self.Meta.model

    def get_primary_key_queryset(self, model):
        return model.objects.all()

    def to_internal_value(self, data):
        rel_field = PrimaryKeyRelatedField(queryset=self.get_primary_key_queryset(self._get_model_class()))
        return rel_field.to_internal_value(data)
