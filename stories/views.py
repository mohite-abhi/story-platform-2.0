from django.shortcuts import render
from django.http import HttpResponse

def story_list(request):
    stories = """
    story1
    story2
    story3
    """
    return HttpResponse(stories)


def story_detail(request, story_id):
    story = f"Story {story_id}"
    return HttpResponse(story)