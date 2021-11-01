from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import datetime

from .models import UserAccount


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


class EmailConfirmationTokenGenerator(PasswordResetTokenGenerator):
    """
    Used to generate 7-digit token for email confirmation.
    """

    # TODO: consider storing tokens into redis temporary storage
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(round_timestamp(timestamp, 5)) + str(user.is_active)

    def make_token(self, user):
        return super().make_token(user)[-7:]

    def check_token(self, user, token):
        return token == self.make_token(user)


class PasswordChangeTokenGenerator(PasswordResetTokenGenerator):
    """
    Used to generate 7-digit token for password reset.
    """

    # TODO: consider storing tokens into redis temporary storage
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(round_timestamp(timestamp, 5)) + str(user.password)

    def make_token(self, user):
        return super().make_token(user)[-7:]

    def check_token(self, user, token):
        return token == self.make_token(user)


class TwoFATokenGenerator(PasswordResetTokenGenerator):
    """
    Used to generate 7-digit token for password reset.
    """

    # TODO: consider storing tokens into redis temporary storage
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(round_timestamp(timestamp, 5))

    def make_token(self, user):
        return super().make_token(user)[-7:]

    def check_token(self, user, token):
        return token == self.make_token(user)
