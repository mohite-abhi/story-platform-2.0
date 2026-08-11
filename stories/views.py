from django.shortcuts import render
from django.http import HttpResponse
from .models import Story

def story_list(request):
    status = request.GET.get('status')
    if status:
        stories = Story.objects.filter(status=status)
    else:
        stories = Story.objects.all()
    stories_output = ""
    for story in stories:
        stories_output += f"<p>{story.id}: {story.title}</p>"

    return HttpResponse(stories_output)


def story_detail(request, story_id):

    try:
        story = Story.objects.get(id=story_id)
    except Story.DoesNotExist:
        return HttpResponse("Story not found", status=404)
    detail = f"<p>Title: {story.title}</p><p>Author: {story.author}</p><p>Status: {story.status}</p><p>Content: {story.content}</p>"
    return HttpResponse(detail)