from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from .models import Video
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class VideoListAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass')

        # create a sample video
        thumb = SimpleUploadedFile('thumb.jpg', b'content', content_type='image/jpeg')
        Video.objects.create(title='Movie Title', description='Movie Description', thumbnail=thumb, category='Drama')

    def test_requires_authentication(self):
        response = self.client.get('/api/video/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_video_list_for_authenticated_user(self):
        token = AccessToken.for_user(self.user)
        # set cookie as CookieJWTAuthentication expects
        self.client.cookies['access_token'] = str(token)

        response = self.client.get('/api/video/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)
        item = response.json()[0]
        self.assertIn('id', item)
        self.assertIn('created_at', item)
        self.assertEqual(item['title'], 'Movie Title')
        self.assertEqual(item['description'], 'Movie Description')
        self.assertEqual(item['category'], 'Drama')
        # thumbnail_url may be None or absolute path - ensure key exists
        self.assertIn('thumbnail_url', item)

    def test_returns_hls_manifest_for_movie(self):
        # create a video and write a sample hls manifest
        video = Video.objects.create(title='HLS Movie', description='desc')
        movie_id = video.id
        resolution = '720p'
        manifest_dir = settings.MEDIA_ROOT / 'hls' / str(movie_id) / resolution
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / 'index.m3u8'
        sample_manifest = b"#EXTM3U\n#EXT-X-VERSION:3\n#EXTINF:10,\nsegment1.ts\n#EXTINF:10,\nsegment2.ts\n"
        manifest_path.write_bytes(sample_manifest)

        token = AccessToken.for_user(self.user)
        self.client.cookies['access_token'] = str(token)

        url = f'/api/video/{movie_id}/{resolution}/index.m3u8'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.apple.mpegurl')
        self.assertEqual(response.content, sample_manifest)
