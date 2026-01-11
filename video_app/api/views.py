import os
from django.conf import settings
from django.http import FileResponse, Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import VideoSerializer
from video_app.models import Video


class VideoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # If URL contains movie_id it's used for streaming - not handled here
        if 'movie_id' in kwargs:
            return Response({'detail': 'Streaming endpoint not handled by this view.'}, status=501)

        videos = Video.objects.all().order_by('-created_at')
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)


class VideoHlsManifestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Handle HLS master playlist: /video/<movie_id>/<resolution>/index.m3u8
        if 'movie_id' in kwargs and 'resolution' in kwargs and request.path.endswith('index.m3u8'):
            movie_id = kwargs.get('movie_id')
            resolution = kwargs.get('resolution')

            base_dir = os.path.normpath(os.path.join(str(settings.MEDIA_ROOT), 'hls'))
            candidate = os.path.normpath(os.path.join(base_dir, str(movie_id), resolution, 'index.m3u8'))

            # prevent path traversal
            if not candidate.startswith(base_dir + os.sep):
                raise Http404('Invalid HLS manifest path')

            if not os.path.exists(candidate):
                raise Http404('HLS manifest not found')

            return FileResponse(open(candidate, 'rb'), content_type='application/vnd.apple.mpegurl')

        return Response({'detail': 'Streaming endpoint not handled by this view.'}, status=501)


class VideoSegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Handle HLS segment: /video/<movie_id>/<resolution>/<segment>/
        if 'movie_id' in kwargs and 'resolution' in kwargs and 'segment' in kwargs:
            movie_id = kwargs.get('movie_id')
            resolution = kwargs.get('resolution')
            segment = kwargs.get('segment')

            base_dir = os.path.normpath(os.path.join(str(settings.MEDIA_ROOT), 'hls'))
            candidate = os.path.normpath(os.path.join(base_dir, str(movie_id), resolution, segment))

            # prevent path traversal
            if not candidate.startswith(base_dir + os.sep):
                raise Http404('Invalid segment path')

            if not os.path.exists(candidate):
                raise Http404('HLS segment not found')

            return FileResponse(open(candidate, 'rb'), content_type='video/mp2t')

        return Response({'detail': 'Invalid segment request.'}, status=400)