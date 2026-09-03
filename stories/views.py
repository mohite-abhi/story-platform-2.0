from django.shortcuts import render, redirect, reverse, get_object_or_404
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
        

def story_edit(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if request.method == "POST":
        story_form = StoryForm(request.POST, instance=story)
        if story_form.is_valid():
            story_form.save()

        else:
            return render(request, "stories/story_edit.html", {"form": story_form, "story_id": story_id})
        
    else:
        story_form = StoryForm(instance=story)

        return render(request, "stories/story_edit.html", {"form": story_form, "story_id": story_id})
    return redirect(reverse("story_detail", args=[story_id]))


def story_delete(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if request.method == "POST":
        story.delete()

    else:
        return render(request, "stories/story_delete.html", {"story_id": story_id})
    return redirect(reverse("story_list"))