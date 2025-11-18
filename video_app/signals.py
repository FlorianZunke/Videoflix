from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os

from .models import Video
from .api.utils import convert_to_480p




@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):

    if created:
        convert_to_480p(instance.video_file.path)


@receiver(post_delete, sender=Video)
def auto_delete_video_on_delete(sender, instance, **kwargs):

    """
    Deletes file from filesystem when corresponding `Video` object is deleted.
    """
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)