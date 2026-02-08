from rest_framework import serializers
from video_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
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

    def get_thumbnail_as_img(self, obj):
        # Need a check up on this, if the thumbnail is not an image, it will break the frontend
        if obj.thumbnail_url:
            return obj.thumbnail_url.url.replace('.png', '.jpg')
        return None