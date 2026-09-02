from django import forms
from .models import Story

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ["title", "content", "status"]

    def clean_title(self):
        title = self.cleaned_data["title"]

        if len(title) < 5:
            raise forms.ValidationError(
                "Title should be at least 5 characters."
            )

        return title