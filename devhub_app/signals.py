import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification, Profile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification)
def push_notification_to_websocket(sender, instance, created, **kwargs):
    if not created:
        return
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    try:
        group_name = f"user_{instance.recipient.id}_notifications"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "content": {
                    "id": instance.id,
                    "title": instance.title,
                    "message": instance.message,
                    "created_at": instance.created_at.isoformat() if instance.created_at else "",
                },
            },
        )
    except Exception:
        logger.warning("WebSocket notification push failed (channel layer may not be available)")


@receiver(post_save, sender=get_user_model())
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            headline="Developer",
            bio="This profile was created automatically.",
            avatar_seed=instance.username,
        )
