from django.shortcuts import render
from django.http import HttpResponse
from .models import Story
from django.contrib.auth import get_user_model
from .forms import StoryForm

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


def story_create(request):

    if request.method == "POST":
        form = StoryForm(request.POST)

        if form.is_valid():
            # cleaned_form = form.cleaned_data

            new_story = form.save(commit=False)

            User = get_user_model()
            user = User.objects.get(id=1)

            new_story.author = user

            new_story.save()

            # Story.objects.create(
            #     title=cleaned_form["title"],
            #     author=user,
            #     content=cleaned_form["content"],
            #     status=cleaned_form["status"]
            # )

            cleaned_form = form.cleaned_data

            response = {
                "title": cleaned_form["title"],
                "content": cleaned_form["content"],
                "status": cleaned_form["status"]
            }
            
            return HttpResponse(str(response))
        
    else:
        form = StoryForm()

    return render(request, "stories/story_create.html", {"form":form})
        