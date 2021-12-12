from django.test import SimpleTestCase, TestCase
from django.db import models
from tests import utils

from utils import normalizers
from utils import serializers
from utils import validators

from user_accounts.serializers import UserAccountSerializer


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


class WriteOnCreationMixinTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = utils.populate_users()

    def test_serialization(self):
        serializer = UserAccountSerializer(instance=self.user)
        self.assertEquals(self.user.department.abbreviation, serializer.data['department']['abbreviation'])

    def test_deserialization(self):
        serializer = UserAccountSerializer(data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testmail@test.com',
            'department': 1
        })
        if serializer.is_valid():
            user = serializer.save()
            self.assertEquals(self.user.department.abbreviation, user.department.abbreviation)


class RegexValidatorTestCase(SimpleTestCase):

    def test_first_capital(self):
        validator = validators.get_regex_validator('test')
        validator('Capitalized')

    def test_hyphen_inside(self):
        validator = validators.get_regex_validator('test')
        validator('Text-with-hyphens')

    def test_whitespaces_inside(self):
        validator = validators.get_regex_validator('test')
        validator('Text with whitespaces')

    def test_numbers_inside(self):
        validator = validators.get_regex_validator('test')
        validator('Numb1ersins1de')

    def test_special_sym_inside(self):
        validator = validators.get_regex_validator('test')
        validator('Hi;.,()!')

    def test_cyrillic(self):
        validator = validators.get_regex_validator('test')
        print(validator.regex)
        validator('Український текст і буква ґ')
