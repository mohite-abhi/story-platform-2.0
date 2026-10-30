from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
import uuid
import os
from django.utils import timezone

class Story(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'

    slug = models.SlugField()
    title = models.CharField(max_length=250)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE)
    content = models.TextField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=100, choices=Status, default=Status.DRAFT)

class Comment(models.Model):
    content = models.TextField(max_length=500)
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



def validate_attachment_file_size(file):
    max_size = 10 * 1024 * 1024  # 10 MiB

    if file.size > max_size:
        from django.core.exceptions import ValidationError

        raise ValidationError(
            "File size cannot exceed 10 MiB."
        )

def story_attachment_upload_to(instance, filename):
    extension = os.path.splitext(filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{extension}"

    now = timezone.now()

    return (
        f"story-attachments/"
        f"{now.year}/"
        f"{now.month:02d}/"
        f"{unique_filename}"
    )

class StoryAttachment(models.Model):
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="story_attachments",
    )
    file = models.FileField(
        upload_to=story_attachment_upload_to,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "png", "jpg", "jpeg"]
            ),
            validate_attachment_file_size,
        ],
    )
    original_filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment {self.pk} for story {self.story_id}"
