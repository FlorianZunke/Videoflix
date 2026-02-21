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

    def get_thumbnail_url_to_img(self, obj):
        if obj.thumbnail_url:
            return obj.thumbnail_url.url
        elif obj.video_url:
            return obj.video_url.url.rsplit('.', 1)[0] + '.jpg'
        return None