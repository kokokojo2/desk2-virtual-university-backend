from django.test import SimpleTestCase
from django.db import models

from utils import normalizers
from utils import serializers


class NormalizerTestCase(SimpleTestCase):

    def test_normalizer(self):
        raw_string = 'SomeBADStRiNg'
        normalized_string = normalizers.Normalizer.first_capital(raw_string)

        self.assertEquals(normalized_string, 'Somebadstring')


class MockModel(models.Model):
    normalized_field = models.TextField()

    class Meta:
        app_label = 'test'
        managed = False


class NormalizedModelSerializerTestCase(SimpleTestCase):

    class BadNormalizedSerializer(serializers.NormalizedModelSerializer):
        class Meta:
            model = MockModel
            normalize_for_type = {str: 'bad_method'}
            fields = '__all__'

    class TypeNormalizedSerializer(serializers.NormalizedModelSerializer):
        class Meta:
            model = MockModel
            normalize_for_type = {str: normalizers.Normalizer.first_capital}
            fields = '__all__'

    class FieldNormalizedSerializer(serializers.NormalizedModelSerializer):
        class Meta:
            model = MockModel
            normalize_for_field = {'normalized_field': normalizers.Normalizer.first_capital}
            fields = '__all__'

    def test_improper_configuration(self):
        self.assertRaises(AttributeError, self.BadNormalizedSerializer)

    def test_normalize_for_type(self):
        serializer = self.TypeNormalizedSerializer(data={'normalized_field': 'BadStRinG'})
        serializer.is_valid()
        self.assertEquals(serializer.data['normalized_field'], 'Badstring')

    def test_normalize_for_field(self):
        serializer = self.FieldNormalizedSerializer(data={'normalized_field': 'BadStRinG'})
        serializer.is_valid()
        self.assertEquals(serializer.data['normalized_field'], 'Badstring')
