from django import forms

class StoryForm(forms.Form):
    title = forms.CharField(max_length=250)
    content = forms.CharField()
    status = forms.CharField(max_length=100)