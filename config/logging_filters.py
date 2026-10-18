
import logging

from .request_context import request_id_var


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()


        # Defaults prevent formatting errors for log records
        # that do not include these optional fields.
        for field in ("story_id", "comment_id", "user_id"):
            if not hasattr(record, field):
                setattr(record, field, "-")
                
        return True
