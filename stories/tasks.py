import logging

from celery import shared_task
from django.core.mail import send_mail

from .models import Comment

logger = logging.getLogger(__name__)


@shared_task
def send_comment_notification(comment_id):
    try:
        comment = (
            Comment.objects
            .select_related(
                "story",
                "story__author",
                "author",
            )
            .get(pk=comment_id)
        )
    except Comment.DoesNotExist:
        logger.warning(
            "Comment notification skipped: comment not found",
            extra={"comment_id": comment_id},
        )
        return "comment_not_found"

    recipient = comment.story.author.email

    if not recipient:
        logger.warning(
            "Comment notification skipped: author has no email",
            extra={
                "comment_id": comment_id,
                "story_id": comment.story_id,
            },
        )
        return "missing_recipient"

    try:
        sent_count = send_mail(
            subject=f"New comment on {comment.story.title}",
            message=(
                f"{comment.author.username} commented on "
                f"'{comment.story.title}':\n\n"
                f"{comment.content}"
            ),
            from_email=None,
            recipient_list=[recipient],
            fail_silently=False,
        )

        if sent_count != 1:
            raise RuntimeError(
                f"Expected one email to be sent; got {sent_count}"
            )

    except Exception:
        logger.exception(
            "Comment notification failed",
            extra={
                "comment_id": comment_id,
                "story_id": comment.story_id,
            },
        )
        raise

    logger.info(
        "Comment notification sent",
        extra={
            "comment_id": comment_id,
            "story_id": comment.story_id,
        },
    )

    return "sent"