from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os
import django_rq

from ..models import Video
from .utils import convert_to_480p, convert_to_360p, convert_to_720p, convert_to_1080p


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):

    if created:
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_to_360p, instance.video_file.path)
        queue.enqueue(convert_to_480p, instance.video_file.path)
        queue.enqueue(convert_to_720p, instance.video_file.path)
        queue.enqueue(convert_to_1080p, instance.video_file.path)


@receiver(post_delete, sender=Video)
def auto_delete_video_on_delete(sender, instance, **kwargs):

    """
    Deletes file from filesystem when corresponding `Video` object is deleted.
    """
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)