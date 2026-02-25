from rest_framework import serializers
from video_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model, includes a method to get the thumbnail URL
    """
    class Meta:
        model = Video
        fields = [
            'id',
            'created_at',
            'title',
            'description',
            'thumbnail_url',
            'category',
        ]

    def get_thumbnail_url_to_img(self, obj):
        """
        Returns the URL of the thumbnail image. If the thumbnail is not available, it generates a URL based on the video URL.
        """
        if obj.thumbnail_url:
            return obj.thumbnail_url.url
        elif obj.video_url:
            return obj.video_url.url.rsplit('.', 1)[0] + '.jpg'
        return None