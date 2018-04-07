import random
import string
from datetime import timedelta
from django.utils import timezone
from django.db import models

from django.contrib.auth.models import User, Group
from base_app.models import BaseAddress, NhanceBaseModel, Profession, Shop
from enhance.constants import SMS_GATEWAY_URL, SMS_GATEWAY_USER, SMS_GATEWAY_PASS, SMS_GATEWAY_SENDER_ID, \
    SMS_GATEWAY_TYPE, SMS_CUSTOMER_HANDOVER_MSG, SMS_CUSTOMER_ACCEPT_MSG
import requests


class ProfileDetails(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name='profile_details')
    role = models.ForeignKey(Group, models.DO_NOTHING, blank=True, null=True)
    qr_code = models.CharField(max_length=254, blank=True, null=True)
    image = models.CharField(max_length=1014, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)

    def __str__(self):
        return str(self.qr_code)


class UserOTP(models.Model):
    id = models.AutoField(primary_key=True)
    mobile_number = models.CharField(max_length=1024)
    otp = models.CharField(max_length=6, null=True, blank=True)
    # created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    # modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    # status = models.IntegerField(default=0)  # 0-inactive, 1-active
    time_stamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def send_otp_as_sms(self, otp_fun=None):
        UserOTP.objects.filter(mobile_number=self.mobile_number).delete()
        self.otp = generate_otp()
        self.save()
        send_sms_to_mobile(self.mobile_number, self.otp, otp_fun)
        return True

    def is_active(self):
        timestamp = timezone.now() - timedelta(seconds=900)
        return self.time_stamp > timestamp


def send_sms_to_mobile(number, otp, otp_fun=None):
    print("send_sms_to_mobilesend_sms_to_mobilesend_sms_to_mobile")
    otp_msg = str(otp)
    if otp_fun == 'handover':
        otp_msg = SMS_CUSTOMER_HANDOVER_MSG.format(otp)
    elif otp_fun == 'accept':
        otp_msg = SMS_CUSTOMER_ACCEPT_MSG.format(otp)
    # url = 'http://193.105.74.159/api/v3/sendsms/plain?user=kapsystem&password=j5SkaRdY&sender=KAPNFO&SMSText=nhnace&type=longsms&GSM=918891586659'
    url = SMS_GATEWAY_URL + 'user=' + SMS_GATEWAY_USER + '&password=' + SMS_GATEWAY_PASS + '&sender=' + SMS_GATEWAY_SENDER_ID + '&SMSText=' + otp_msg + '&type=' + SMS_GATEWAY_TYPE + '&GSM=91' + str(number)
    response = requests.get(url)


def generate_otp(size=6, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class AddressForUser(BaseAddress):
    user = models.OneToOneField(
        User, on_delete=models.DO_NOTHING, related_name="user_address")

    def __str__(self):
        return str(self.user)


class CustomerDetail(NhanceBaseModel):
    FEMALE = 'female'
    MALE = 'male'
    CHOICES = (
        (FEMALE, 'female'),
        (MALE, 'male'),

    )
    profession = models.ForeignKey(Profession, models.DO_NOTHING, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    user = models.OneToOneField(
        ProfileDetails, on_delete=models.DO_NOTHING, related_name="customer_details")
    favourite_shop = models.ForeignKey(Shop, models.DO_NOTHING, blank=True, null=True, )
    gender = models.CharField(max_length=6, choices=CHOICES, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    referral_code = models.CharField(max_length=256, null=True, blank=True)
    referred_code = models.CharField(max_length=256, null=True, blank=True)
    is_referred = models.BooleanField(default=False)
    def __str__(self):
        return str(self.user)
