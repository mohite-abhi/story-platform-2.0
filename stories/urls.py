from django.urls import path, include
from . import views

from rest_framework.routers import DefaultRouter

# from .views import StoryListAPIView, StoryDetailAPIView
from .views import StoryViewSet

router = DefaultRouter()

router.register(
    r"stories",
    StoryViewSet,
    basename="story"
)

urlpatterns = [
    path('', views.story_list, name='story_list'),
    path('create/', views.story_create, name='story_create'),
    path('<int:story_id>/', views.story_detail, name='story_detail'),
    path('<int:story_id>/edit/', views.story_edit, name='story_edit'),
    path('<int:story_id>/delete/', views.story_delete, name='story_delete'),
    path('api/', include(router.urls))
    # path('api/stories/', StoryListAPIView.as_view(), name="story-list"),
    # path('api/stories/<int:pk>', StoryDetailAPIView.as_view(), name='story-detail')
]