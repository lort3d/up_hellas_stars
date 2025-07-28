from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Character, Film, Starship


@receiver(post_save, sender=Character)
@receiver(post_save, sender=Film)
@receiver(post_save, sender=Starship)
@receiver(post_delete, sender=Character)
@receiver(post_delete, sender=Film)
@receiver(post_delete, sender=Starship)
def invalidate_cache(sender, **kwargs):
    """
    Invalidate the entire cache when any model instance is saved or deleted.
    This ensures that GET requests will fetch fresh data after any modification.
    """
    cache.clear()