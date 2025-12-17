from django.urls import path

from .views import VideoView


urlpatterns = [
    path('video/', VideoView.as_view(), name ='video'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoView.as_view(), name='video_stream'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', VideoView.as_view(), name='video_segment'),
]
