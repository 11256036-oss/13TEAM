from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User, dispatch_uid="course.ensure_profile_once")
def ensure_profile(sender, instance, created, **kwargs):
    # 只在第一次建立 User 時建立 Profile（不會重複）
    if created:
        Profile.objects.get_or_create(
            user=instance,
            defaults={"role": "student", "full_name": instance.username},
        )
