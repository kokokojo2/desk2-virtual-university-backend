from datetime import datetime

from django.core.exceptions import ImproperlyConfigured
import redis

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings

from .models import UserAccount

if settings.REDIS_STORED_TOKENS:
    redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_TOKENS_STORAGE)


def round_timestamp(timestamp, minute):
    """
    This method is used to round timestamp to a particular minute ending.
    This is useful to create a token that will be valid for a particular time.
    :param timestamp: raw timestamp
    :return: rounded timestamp
    """
    raw_datetime = datetime.fromtimestamp(timestamp)
    round_to_minutes = raw_datetime.replace(
        second=0,
        microsecond=0,
        minute=raw_datetime.minute - raw_datetime.minute % minute
    )

    return datetime.timestamp(round_to_minutes)


def check_token(token_gen_class, email, token):
    token_generator = token_gen_class()
    try:
        user = UserAccount.objects.get(email=email)
    except (TypeError, ValueError, OverflowError, UserAccount.DoesNotExist):
        user = None

    return user and token_generator.check_token(user, token)


class RedisTokenMixin:
    """
    Provides functionality for storing tokens in redis storage.
    """
    def _get_redis_key_basename(self):
        try:
            return getattr(self, 'redis_key_basename')
        except AttributeError:
            raise ImproperlyConfigured('Token generator that inherits from RedisTokenMixin class'
                                       ' requires redis_key_basename class variable to be defined.')

    def _get_token_length(self):
        try:
            return getattr(self, 'token_length')
        except AttributeError:
            raise ImproperlyConfigured('Token generator that inherits from RedisTokenMixin class'
                                       ' requires token_length class variable to be defined.')

    def _get_token_timeout(self):
        try:
            return getattr(self, 'token_timeout')
        except AttributeError:
            raise ImproperlyConfigured('Token generator that inherits from RedisTokenMixin class'
                                       ' requires token_timeout class variable to be defined.')

    def make_token(self, user):
        token = super().make_token(user)[-self._get_token_length():]
        if settings.REDIS_STORED_TOKENS:
            redis_client.set(
                str(self._get_redis_key_basename() + '_' + str(user.pk)),
                token,
                ex=self._get_token_timeout()
            )

        return token

    def check_token(self, user, token, remove_from_storage=False):
        if settings.REDIS_STORED_TOKENS:
            redis_key_name = self._get_redis_key_basename() + '_' + str(user.pk)
            genuine_token = redis_client.get(redis_key_name)
            if not genuine_token:
                return False

            genuine_token = genuine_token.decode('utf-8')
            if remove_from_storage:
                redis_client.delete(redis_key_name)

            return token == genuine_token

        return token == self.make_token(user)


class EmailConfirmationTokenGenerator(RedisTokenMixin, PasswordResetTokenGenerator):
    """
    Used to generate 7-digit token for email confirmation.
    """
    redis_key_basename = 'email'
    token_length = settings.EMAIL_CONFIRM_TOKEN_LENGTH
    token_timeout = settings.EMAIL_CONFIRM_TOKEN_TIMEOUT

    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(round_timestamp(timestamp, 5)) + str(user.is_active)


class EmailConfirmationUnregisteredTokenGenerator(PasswordResetTokenGenerator):
    """Used to generate tokens to confirm emails independent of user model."""
    token_length = settings.EMAIL_CONFIRM_TOKEN_LENGTH
    token_timeout = settings.EMAIL_CONFIRM_TOKEN_TIMEOUT
    basename = 'unregistered'

    def make_token(self, email):
        token = super().make_token(email)[-self.token_length:]
        if settings.REDIS_STORED_TOKENS:
            redis_client.set(
                str(self.basename + '_' + email),
                token,
                ex=self.token_timeout
            )

        return token

    def check_token(self, email, token, remove_from_storage=False):
        if settings.REDIS_STORED_TOKENS:
            redis_key_name = self.basename + '_' + str(email)
            genuine_token = redis_client.get(redis_key_name)
            if not genuine_token:
                return False

            genuine_token = genuine_token.decode('utf-8')
            if remove_from_storage:
                redis_client.delete(redis_key_name)

            return token == genuine_token

        return token == self.make_token(email)

    def _make_hash_value(self, email, timestamp):
        return str(email) + str(round_timestamp(timestamp, 5))


class PasswordChangeTokenGenerator(RedisTokenMixin, PasswordResetTokenGenerator):
    """
    Used to generate 7-digit token for password reset.
    """
    redis_key_basename = 'password'
    token_length = settings.PASSWORD_RESET_TOKEN_LENGTH
    token_timeout = settings.PASSWORD_RESET_TOKEN_TIMEOUT

    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(round_timestamp(timestamp, 5)) + str(user.password)


class TwoFATokenGenerator(RedisTokenMixin, PasswordResetTokenGenerator):
    """
    Used to generate 7-digit token for password reset.
    """
    redis_key_basename = '2fa'
    token_length = settings.TWO_FA_TOKEN_LENGTH
    token_timeout = settings.TWO_FA_TOKEN_TIMEOUT

    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(round_timestamp(timestamp, 5))
