from django.shortcuts import render
from django.http import HttpResponse
from .models import Story

def story_list(request):
    status = request.GET.get('status')
    if status:
        stories = Story.objects.filter(status=status)
    else:
        stories = Story.objects.all()

    return render(request, 'stories/story_list.html', {'stories': stories})


def story_detail(request, story_id):
    try:
        story = Story.objects.get(id=story_id)
    except Story.DoesNotExist:
        return HttpResponse("Story not found", status=404)
        
    return render(request, 'stories/story_detail.html', {'story': story})