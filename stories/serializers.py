from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Story, Comment

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