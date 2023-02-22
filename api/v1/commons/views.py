from django.shortcuts import render
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

from api.v1.users.services import make_errors


def string_to_date(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d").replace(
        tzinfo=timezone.get_current_timezone()
    )


def get_serializer_errors(serializer):
    raise ValidationError(message=f'{make_errors(serializer.errors)}')


def return_serializer_errors(serializer):
    return make_errors(serializer.errors)


def not_serializer_is_valid(serializer):
    return {
        "success": False,
        "message": 'Error occurred.',
        "error": make_errors(serializer.errors),
        "data": [],
    }


def get_error_response(error):
    return {
        "success": False,
        "message": error,
        "error": 'Error occurred.',
        "data": [],
    }


def serializer_valid_response(serializer):
    return {
        "success": True,
        "message": 'Data created successfully.',
        "error": [],
        "data": serializer.data,
    }


def get_valid_response():
    return {
        "success": True,
        "message": 'Successfully done.',
        "error": [],
        "data": [],
    }


def serializer_update_valid_response(serializer):
    return {
        "success": True,
        "message": 'Data updated successfully.',
        "error": [],
        "data": serializer.data,
    }


def get_serializer_valid_response(serializer):
    return {
        "success": True,
        "message": 'Data got successfully.',
        "error": [],
        "data": serializer.data,
    }


def exception_response(e):
    return {
        "success": False,
        "message": 'Error occurred.',
        "error": str(e),
        "data": [],
    }


def raise_exception_response(e):
    raise ValidationError(message=f'{e}')


def object_not_found_response():
    return {
        "success": False,
        "message": 'Object not found.',
        "error": "Error occurred.",
        "data": [],
    }


def object_deleted_response():
    return {
        "success": False,
        "message": 'Objects deleted successfully.',
        "error": [],
        "data": [],
    }

