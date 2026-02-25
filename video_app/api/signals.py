from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import post_save, post_delete
import os
import django_rq

from ..models import Video
from .utils import convert_and_save


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for `post_save` signal of `Video` model.
    It updates the `conversion_status` field to 'processing' and enqueues the `convert_and_save` function to be executed in the background using RQ.
    """
    if created:
        Video.objects.filter(pk=instance.pk).update(conversion_status='processing')

        transaction.on_commit(lambda: django_rq.enqueue(convert_and_save, instance.id))


@receiver(post_delete, sender=Video)
def auto_delete_video_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem when corresponding `Video` object is deleted.
    """
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)