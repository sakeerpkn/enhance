import random
import string
from _pydecimal import Decimal
from datetime import datetime

from django.utils import timezone

from api.api_baggage.models import CustomerBag
from api.api_ern_burn.models import Summary, EarnTransaction, EarnActionDetail
from api.api_user.models import CustomerDetail, ProfileDetails


def earned_points_greater_burned_points(burned_points, user):
    try:
        summary = Summary.objects.get(user=user)
        if Decimal(summary.balance_points) >= Decimal(burned_points):
            return True
    except Summary.DoesNotExist:
        pass

    return False


def earn_points(user, action):
    try:
        earn_action = EarnActionDetail.objects.get(name=action)
        EarnTransaction.objects.get_or_create(user=user, erned_action=earn_action,
                                              defaults={'erned_points': earn_action.points})
        return True
    except EarnActionDetail.DoesNotExist:
        pass
    return False


def user_qrcode():
    while True:
        qr = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        if ProfileDetails.objects.filter(qr_code=qr).exists():continue
        else: break
    return qr


def membership_completion_percentage(user):
    summary = Summary.objects.get(user=user)
    if summary.membership.slab_starts == summary.membership.slab_ends:
        return 0
    slab_diff = summary.membership.slab_ends - summary.membership.slab_starts
    return (summary.total_ern_points / slab_diff) * 100


def profile_completion_percentage(user, customer):
    field = 0
    total_fields = 7
    if user.email:
        field = field + 1
    if customer.gender:
        field = field + 1
    if customer.address:
        field = field + 1
    if customer.profession:
        field = field + 1
    if customer.favourite_shop:
        field = field + 1
    if customer.date_of_birth:
        field = field + 1
    return (field / total_fields) * 100


def check_bag_transaction_active(user):
    if CustomerBag.objects.filter(customer_id=user.username, parent_id__isnull=True, status=0):
        return True
    return False


def generate_customer_referral_code():
    '''Create the referral code. '''
    while (True):
        ref_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        if CustomerDetail.objects.filter(referral_code=ref_code).exists(): continue
        else: break
    return ref_code


def earn_referral_points(user):
    '''
    Add referral earn points
    '''
    try:
        earn_action = EarnActionDetail.objects.get(name='Customer Referral')
        EarnTransaction.objects.create(user=user, erned_points=earn_action.points,erned_action=earn_action)
    except:return False
    return True

def check_coupon_expired(coupon):
    if coupon.validity_date < timezone.now():
        return True
    return False