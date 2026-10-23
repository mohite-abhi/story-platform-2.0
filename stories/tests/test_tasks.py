
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings

from stories.models import Comment, Story
from stories.tasks import send_comment_notification

from types import SimpleNamespace
from unittest.mock import Mock, patch

from celery.exceptions import Retry

from stories.views import StoryCommentListCreateAPIView

@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
class CommentNotificationTaskTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.author = User.objects.create_user(
            username="story_author",
            password="password123",
            email="author@example.com",
        )

        cls.commenter = User.objects.create_user(
            username="commenter",
            password="password123",
            email="commenter@example.com",
        )

        cls.story = Story.objects.create(
            title="Notification Test Story",
            content="Story content",
            status=Story.Status.PUBLISHED,
            author=cls.author,
        )

        cls.comment = Comment.objects.create(
            content="This is a test comment",
            story=cls.story,
            author=cls.commenter,
        )

    def test_sends_notification_to_story_author(self):
        result = send_comment_notification(
            self.comment.pk
        )

        self.assertEqual(result, "sent")
        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]

        self.assertEqual(
            message.to,
            [self.author.email],
        )
        self.assertEqual(
            message.subject,
            f"New comment on {self.story.title}",
        )
        self.assertIn(
            self.commenter.username,
            message.body,
        )
        self.assertIn(
            self.story.title,
            message.body,
        )
        self.assertIn(
            self.comment.content,
            message.body,
        )

    def test_missing_comment_is_handled_safely(self):
        result = send_comment_notification(
            999999
        )

        self.assertEqual(result, "comment_not_found")
        self.assertEqual(len(mail.outbox), 0)


    @patch("stories.tasks.send_mail")
    def test_missing_recipient_skips_notification(
        self, mock_send_mail
    ):
        self.author.email = ""
        self.author.save(update_fields=["email"])

        result = send_comment_notification(
            self.comment.pk
        )

        self.assertEqual(result, "missing_recipient")
        mock_send_mail.assert_not_called()


    @patch(
        "stories.tasks.send_mail",
        side_effect=ValueError("Invalid email configuration"),
    )
    def test_unexpected_email_failure_is_not_retried(self, mock_send_mail):
        with patch.object(send_comment_notification, "retry") as mock_retry:
            with self.assertRaises(ValueError):
                send_comment_notification(self.comment.pk)

        mock_send_mail.assert_called_once()
        mock_retry.assert_not_called()


    @patch(
        "stories.tasks.send_mail",
        side_effect=TimeoutError("Temporary email failure"),
    )
    def test_transient_email_failure_requests_retry(self, mock_send_mail):
        with patch.object(
            send_comment_notification,
            "retry",
            side_effect=Retry("Retry requested"),
        ) as mock_retry:
            with self.assertRaises(Retry):
                send_comment_notification(self.comment.pk)

        mock_send_mail.assert_called_once()
        mock_retry.assert_called_once()

        retry_exception = mock_retry.call_args.kwargs["exc"]
        self.assertIsInstance(retry_exception, TimeoutError)


    @patch("stories.views.send_comment_notification.delay")
    def test_notification_is_queued_only_after_commit(self, mock_delay):
        view = StoryCommentListCreateAPIView()
        view.request = SimpleNamespace(user=self.commenter)
        view.kwargs = {"story_id": self.story.pk}

        serializer = Mock()
        serializer.save.return_value = self.comment

        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            view.perform_create(serializer)

            mock_delay.assert_not_called()

        self.assertEqual(len(callbacks), 1)

        callbacks[0]()

        mock_delay.assert_called_once_with(self.comment.pk)