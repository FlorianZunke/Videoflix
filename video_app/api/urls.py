from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import VideoListView, VideoHlsManifestView, VideoSegmentView


router = DefaultRouter()
router.register(r'video', VideoListView, basename='video')
urlpatterns = router.urls

urlpatterns += [
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoHlsManifestView.as_view(), name='video_stream'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', VideoSegmentView.as_view(), name='video_segment'),
]
