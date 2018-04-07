from django.db.models.signals import post_save
from django.dispatch import receiver

from api.api_ern_burn.models import EarnTransaction, EarnBurnTransaction, Summary, EARN, BurnTransaction, BURN
from api.api_user.models import CustomerDetail
from base_app.models import StatusLevel


@receiver(post_save, sender=EarnTransaction)
def create_earn_burn_transaction_for_earn(sender, instance, created, **kwargs):
    if created:
        summary, created = Summary.objects.get_or_create(user=instance.user, defaults={'user': instance.user})
        if created:
            summary.membership = StatusLevel.objects.get(slab_starts=0)
        EarnBurnTransaction.objects.create(user=instance.user, opening_points=summary.total_ern_points,
                                           transaction_type=EARN, transaction_id=instance.id,
                                           transfer_points=instance.erned_points)
        summary.total_ern_points = summary.total_ern_points + instance.erned_points
        levels = StatusLevel.objects.filter(slab_ends__lte=summary.total_ern_points).order_by('-slab_ends')
        if levels:
            summary.membership = levels[0]
        summary.save()


@receiver(post_save, sender=BurnTransaction)
def create_earn_burn_transaction_for_burn(sender, instance, created, **kwargs):
    if created:
        summary, created = Summary.objects.get_or_create(user=instance.user, defaults={'user': instance.user})
        EarnBurnTransaction.objects.create(user=instance.user, opening_points=summary.total_ern_points,
                                           transaction_type=BURN, transaction_id=instance.id,
                                           transfer_points=instance.burned_points)
        summary.total_burn_points = summary.total_burn_points + instance.burned_points
        summary.save()


@receiver(post_save, sender=CustomerDetail)
def create_summary(sender, instance, created, **kwargs):
    if created:
        summary, created = Summary.objects.get_or_create(user=instance.user.user_id,
                                                         defaults={'user': instance.user.user_id})
        if created:
            summary.membership = StatusLevel.objects.get(slab_starts=0)
        summary.save()
