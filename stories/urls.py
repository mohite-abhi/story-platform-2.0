from django.urls import path
from . import views

from .views import story_list_api

urlpatterns = [
    path('', views.story_list, name='story_list'),
    path('create/', views.story_create, name='story_create'),
    path('<int:story_id>/', views.story_detail, name='story_detail'),
    path('<int:story_id>/edit/', views.story_edit, name='story_edit'),
    path('<int:story_id>/delete/', views.story_delete, name='story_delete'),
    path('api/stories/', story_list_api, name="story-list-api")
]