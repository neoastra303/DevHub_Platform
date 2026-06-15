from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification


@receiver(post_save, sender=Notification)
def push_notification_to_websocket(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
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
        pass
