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

    def get_thumbnail(self, obj):
        """
        Return the absolute URL for the thumbnail if it exists, otherwise return None
        """
        if obj.thumbnail_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail_url.url)
            return obj.thumbnail_url.url
        return None