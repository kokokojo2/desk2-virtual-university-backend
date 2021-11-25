from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError


def view_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, IntegrityError) and not response:
        response = Response({'detail': context['view'].db_exception_msg}, status=status.HTTP_400_BAD_REQUEST)

    return response
