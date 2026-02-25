import os
from django.conf import settings
from django.http import FileResponse, Http404

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import VideoSerializer
from video_app.models import Video
from auth_app.api.authentication import CookieJWTAuthentication


class VideoListView(ListModelMixin, GenericViewSet):
    """
    ViewSet for listing all videos. It requires authentication and uses the `VideoSerializer` to serialize the video data.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    queryset = Video.objects.all().order_by('-created_at')
    serializer_class = VideoSerializer


class VideoHlsManifestView(APIView):
    """
    View for serving HLS master playlist and segments. It checks the requested path for the movie ID, resolution, and segment, validates the path to prevent directory traversal attacks, and serves the appropriate file if it exists.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, *args, **kwargs):
        """
        Handle HLS manifest: /video/<movie_id>/<resolution>/index.m3u8
        """
        if 'movie_id' in kwargs and 'resolution' in kwargs and request.path.endswith('index.m3u8'):
            movie_id = kwargs.get('movie_id')
            resolution = kwargs.get('resolution')

            base_dir = os.path.normpath(
                os.path.join(str(settings.MEDIA_ROOT), 'hls'))
            candidate = os.path.normpath(os.path.join(
                base_dir, str(movie_id), resolution, 'index.m3u8'))

            if not candidate.startswith(base_dir + os.sep):
                raise Http404('Invalid HLS manifest path')

            if not os.path.exists(candidate):
                raise Http404('HLS manifest not found')

            return FileResponse(open(candidate, 'rb'), content_type='application/vnd.apple.mpegurl')

        return Response({'detail': 'Streaming endpoint not handled by this view.'}, status=501)


class VideoSegmentView(APIView):
    """
    View for serving HLS segments. It checks the requested path for the movie ID, resolution, and segment, validates the path to prevent directory traversal attacks, and serves the appropriate file if it exists.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, *args, **kwargs):
        """
        Handle HLS segments: /video/<movie_id>/<resolution>/<segment>
        """
        if 'movie_id' in kwargs and 'resolution' in kwargs and 'segment' in kwargs:
            movie_id = kwargs.get('movie_id')
            resolution = kwargs.get('resolution')
            segment = kwargs.get('segment')

            base_dir = os.path.normpath(
                os.path.join(str(settings.MEDIA_ROOT), 'hls'))
            candidate = os.path.normpath(os.path.join(
                base_dir, str(movie_id), resolution, segment))

            if not candidate.startswith(base_dir + os.sep):
                raise Http404('Invalid segment path')

            if not os.path.exists(candidate):
                raise Http404('HLS segment not found')

            return FileResponse(open(candidate, 'rb'), content_type='video/mp2t')

        return Response({'detail': 'Invalid segment request.'}, status=400)
