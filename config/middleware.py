
import uuid

from .request_context import request_id_var


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = uuid.uuid4().hex
        token = request_id_var.set(request.request_id)

        try:
            response = self.get_response(request)
            response["X-Request-ID"] = request.request_id
            return response
        finally:
            request_id_var.reset(token)
