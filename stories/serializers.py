import os

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Story, Comment, StoryAttachment

import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username"]

class StorySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Story
        fields = ["id", "title", "content", "status", "author"]
        read_only_fields = ["id"]

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "content", "story", "author", "created_at", "updated_at"]
        read_only_fields = ["id", "story", "author", "created_at", "updated_at"]



class StoryAttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    story_id = serializers.IntegerField(read_only=True)
    filename = serializers.CharField(
        source="original_filename",
        read_only=True,
    )

    class Meta:
        model = StoryAttachment
        fields = [
            "id",
            "story_id",
            "filename",
            "file",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "story_id",
            "filename",
            "created_at",
        ]

    def validate_file(self, uploaded_file):
        max_size = 10 * 1024 * 1024  # 10 MiB

        if uploaded_file.size > max_size:
            raise serializers.ValidationError(
                "File size cannot exceed 10 MiB."
            )

        # Normalize Windows-style paths as well as Unix-style paths.
        filename = uploaded_file.name.replace("\\", "/").rsplit("/", 1)[-1]
        extension = os.path.splitext(filename)[1].lower()

        allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg"}

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                "Only PDF, PNG, and JPEG files are allowed."
            )

        # Check the file signature, not just the extension.
        uploaded_file.seek(0)
        header = uploaded_file.read(8)
        uploaded_file.seek(0)

        valid_signatures = {
            ".pdf": header.startswith(b"%PDF-"),
            ".png": header.startswith(b"\x89PNG\r\n\x1a\n"),
            ".jpg": header.startswith(b"\xff\xd8\xff"),
            ".jpeg": header.startswith(b"\xff\xd8\xff"),
        }

        if not valid_signatures[extension]:
            raise serializers.ValidationError(
                "The file content does not match its extension."
            )

        return uploaded_file


    def create(self, validated_data):
        uploaded_file = validated_data["file"]

        original_filename = uploaded_file.name.replace(
            "\\", "/"
        ).rsplit("/", 1)[-1]

        validated_data["original_filename"] = original_filename

        attachment = StoryAttachment(**validated_data)

        try:
            attachment.save()
        except Exception:
            # FileField may already have uploaded the object to S3
            # before the PostgreSQL insert failed.
            stored_name = attachment.file.name

            if stored_name:
                try:
                    attachment.file.storage.delete(stored_name)
                except Exception:
                    logger.exception(
                        "Failed to clean up attachment after save failure",
                        extra={
                            "story_id": attachment.story_id,
                            "user_id": attachment.uploaded_by_id,
                        },
                    )

            raise

        return attachment

