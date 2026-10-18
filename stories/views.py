from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Story, Comment
from django.contrib.auth.decorators import login_required
from .forms import StoryForm


from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import StorySerializer, CommentSerializer

from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsStoryAuthor, IsCommentAuthor

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from rest_framework.exceptions import ValidationError

from rest_framework.viewsets import ModelViewSet

from rest_framework import mixins, viewsets

from django.core.cache import cache
from stories.cache_utils import safe_cache_get, safe_cache_set, safe_cache_delete

import logging

logger = logging.getLogger(__name__)


def story_list(request):
    status = request.GET.get('status')
    if status:
        stories = Story.objects.filter(status=status)
    else:
        stories = Story.objects.all()

    return render(request, 'stories/story_list.html', {'stories': stories})


def story_detail(request, story_id):
    story = get_object_or_404(Story, id=story_id)        
    return render(request, 'stories/story_detail.html', {'story': story})


@login_required
def story_create(request):

    if request.method == "POST":
        form = StoryForm(request.POST)

        if form.is_valid():
            new_story = form.save(commit=False)
            new_story.author = request.user
            new_story.save()
            return redirect(reverse("story_detail", args=[new_story.id]))

    else:
        form = StoryForm()

    return render(request, "stories/story_create.html", {"form":form})
        

@login_required
def story_edit(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    if story.author != request.user:
        return HttpResponseForbidden("Forbidden")

    if request.method == "POST":
        story_form = StoryForm(request.POST, instance=story)
        if story_form.is_valid():
            story_form.save()
            return redirect(reverse("story_detail", args=[story_id]))
        else:
            return render(request, "stories/story_edit.html", {"form": story_form, "story_id": story_id})        
    else:
        story_form = StoryForm(instance=story)

        return render(request, "stories/story_edit.html", {"form": story_form, "story_id": story_id})


@login_required
def story_delete(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    if story.author != request.user:
        return HttpResponseForbidden("Forbidden")

    if request.method == "POST":
        story.delete()
    else:
        return render(request, "stories/story_delete.html", {"story_id": story_id})

    return redirect(reverse("story_list"))

# API Views
# class StoryListAPIView(ListCreateAPIView):
#     # queryset = Story.objects.all().order_by("id")
#     serializer_class = StorySerializer

#     allowed_ordering_fields = {
#         "id",
#         "title",
#         "created_at",
#         "updated_at",
#     }


#     def get_queryset(self):
#         queryset = Story.objects.all()

#         status = self.request.query_params.get("status")
#         ordering = self.request.query_params.get("ordering")


#         if status:
#             if status not in Story.Status.values:
#                 raise ValidationError({
#                     "status": "Invalid status."
#                 })
#             queryset = queryset.filter(status=status)

#         if ordering:
#             ordering_field = ordering.lstrip("-")
#             if ordering_field not in self.allowed_ordering_fields:
#                 raise ValidationError({
#                     "ordering": "Invalid ordering field."
#                 })
#             queryset = queryset.order_by(ordering, "id")

#         else:
#             queryset = queryset.order_by("id")

#         return queryset


#     def get_permissions(self):
#         if self.request.method == "POST":
#             return [IsAuthenticated()]
        
#         return [AllowAny()]

#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)


# class StoryDetailAPIView(RetrieveUpdateDestroyAPIView):

#     queryset = Story.objects.all()
#     serializer_class = StorySerializer

#     def get_permissions(self):
#         if self.request.method == "GET":
#             return [AllowAny()]

#         return [IsStoryAuthor()]


def story_detail_cache_key(story_id):
    return f"story:detail:v1:{story_id}"

# ViewSets
class StoryViewSet(ModelViewSet):

    serializer_class = StorySerializer

    allowed_ordering_fields = {
        "id",
        "title",
        "created_at",
        "updated_at",
    }

    def get_queryset(self):
        # queryset = Story.objects.all()
        queryset = Story.objects.select_related("author")


        status = self.request.query_params.get("status")
        ordering = self.request.query_params.get("ordering")


        if status:
            if status not in Story.Status.values:
                raise ValidationError({
                    "status": ["Invalid status."]
                })
            queryset = queryset.filter(status=status)

        if ordering:
            ordering_field = ordering.lstrip("-")
            if ordering_field not in self.allowed_ordering_fields:
                raise ValidationError({
                    "ordering": ["Invalid ordering field."]
                })
            queryset = queryset.order_by(ordering, "id")

        else:
            queryset = queryset.order_by("id")

        return queryset

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]

        if self.action == "list":
            return [AllowAny()]

        if self.action == "retrieve":
            return [AllowAny()]

        return [IsStoryAuthor()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

        logger.info(
            "Story created",
            extra={
                "story_id": serializer.instance.pk,
                "user_id": self.request.user.pk,
            },
        )


    def retrieve(self, request, *args, **kwargs):
        story_id = self.kwargs[self.lookup_field]
        cache_key = story_detail_cache_key(story_id)
        
        cached_data = safe_cache_get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)

        if response.status_code == 200:
            
            safe_cache_set(cache_key, response.data, timeout=300)

        return response

    def perform_update(self, serializer):
        instance = serializer.save()
        safe_cache_delete(story_detail_cache_key(instance.pk))

        logger.info(
            "Story updated",
            extra={
                "story_id": instance.pk,
                "user_id": self.request.user.pk,
            },
        )


    def perform_destroy(self, instance):
        story_id = instance.pk
        super().perform_destroy(instance)
        safe_cache_delete(story_detail_cache_key(story_id))

        logger.info(
            "Story deleted",
            extra={
                "story_id": story_id,
                "user_id": self.request.user.pk,
            },
        )

class CommentViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.select_related("author")

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        if self.action == "create":
            return [IsAuthenticated()]

        return [IsCommentAuthor()]

class StoryCommentListCreateAPIView(ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_story(self):
        return get_object_or_404(
            Story,
            id=self.kwargs["story_id"],
        )

    def get_queryset(self):
        story = self.get_story()

        return (
            Comment.objects
            .select_related("author")
            .filter(story=story)
            .only(
                "id",
                "content",
                "story_id",
                "author_id",
                "created_at",
                "updated_at",
                "author__id",
                "author__username",
            )
            .order_by("id")
        )

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        story = self.get_story()

        comment = serializer.save(
            story=story,
            author = self.request.user
        )

        logger.info(
            "Comment created",
            extra={
                "comment_id": comment.pk,
                "story_id": story.pk,
                "user_id": self.request.user.pk,
            },
        )