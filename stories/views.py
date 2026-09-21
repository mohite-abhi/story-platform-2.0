from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Story
from django.contrib.auth.decorators import login_required
from .forms import StoryForm


from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import StorySerializer

from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsStoryAuthor

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


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


# class StoryListAPIView(APIView):
    
#     def get_permissions(self):
#         if self.request.method == "POST":
#             return [IsAuthenticated()]
        
#         return [AllowAny()]

#     def get(self, request):
#         stories = Story.objects.all()
#         serializer = StorySerializer(stories, many=True)

#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )


#     def post(self, request):
#         serializer = StorySerializer(data=request.data)

#         serializer.is_valid(raise_exception=True)

#         story = serializer.save(author=request.user)

#         return Response(
#             StorySerializer(story).data,
#             status=status.HTTP_201_CREATED
#         )


class StoryListAPIView(ListCreateAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# class StoryDetailAPIView(APIView):

#     def get_permissions(self):
#         if self.request.method == "GET":
#             return [AllowAny()]
        
#         return [IsStoryAuthor()]


#     def get(self, request, pk):
#         try:
#             story = Story.objects.get(pk=pk)
#         except Story.DoesNotExist:
#             return Response(
#                 {"detail": "Story not found."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         serializer = StorySerializer(story)

#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )


#     def patch(self, request, pk):
#         try:
#             story = Story.objects.get(pk=pk)
#         except Story.DoesNotExist:
#             return Response(
#                 {"detail": "Story not found."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         self.check_object_permissions(request, story)

#         serializer = StorySerializer(
#             story,
#             data=request.data,
#             partial=True
#         )

#         serializer.is_valid(raise_exception=True)

#         serializer.save()

#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )


#     def delete(self, request, pk):
#         try:
#             story = Story.objects.get(pk=pk)
#         except Story.DoesNotExist:
#             return Response(
#                 {"detail": "Story not found."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         self.check_object_permissions(request, story)

#         story.delete()

#         return Response(status=status.HTTP_204_NO_CONTENT)


#     def put(self, request, pk):
#         try:
#             story = Story.objects.get(pk=pk)
#         except Story.DoesNotExist:
#             return Response(
#                 {"detail": "Story not found."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         self.check_object_permissions(request, story)

#         serializer = StorySerializer(
#             story,
#             data=request.data
#         )

#         serializer.is_valid(raise_exception=True)

#         serializer.save()

#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )



class StoryDetailAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Story.objects.all()
    serializer_class = StorySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsStoryAuthor()]