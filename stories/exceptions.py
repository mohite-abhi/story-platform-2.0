from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None

    if isinstance(exc, APIException):
        response.data["code"] = exc.default_code
    elif response.status_code == 404:
        response.data["code"] = "not_found"
        
    return response