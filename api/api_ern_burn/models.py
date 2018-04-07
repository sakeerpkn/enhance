from django.db import models

# Create your models here.
from django.contrib.auth.models import User

from base_app.models import StatusLevel, Shop, NhanceBaseModel

EARN = 'Earn'
BURN = 'Burn'
DATE = 'Date'
PERIOD = 'Period'
NO_VALIDITY= 'No Validity'
TRANSACTION_CHOICES = (
    (EARN, 'Earn'),
    (BURN, 'Burn')
)

VALIDITY_CHOICES = (
    (DATE, 'Date'),
    (PERIOD, 'Period'),
    (NO_VALIDITY, 'No Validity')
)


class EarnActionDetail(models.Model):
    action_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    validity_type = models.CharField(choices=VALIDITY_CHOICES, max_length=20)
    validity_days = models.IntegerField(blank=True, null=True)
    validity_date = models.DateTimeField(blank=True, null=True)
    created_user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,
                                     related_name="ern_action_created_user_id")
    modified_user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,
                                      related_name="ern_action_modified_user_id")
    created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    status = models.IntegerField(default=1)  # 0-inactive, 1-active
    shop = models.ForeignKey(Shop, null=True, blank=True, related_name="earn_coupons")

    points = models.FloatField(default=0.00)
    terms_and_conditions = models.TextField(null=True)
    image = models.ImageField(upload_to='shop_earns', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)

    # is_viewed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class BurnActionDetail(models.Model):
    action_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    validity_type = models.CharField(choices=VALIDITY_CHOICES, default=DATE, max_length=6)
    validity_days = models.IntegerField(blank=True, null=True)
    validity_date = models.DateTimeField(blank=True, null=True)
    created_user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,
                                     related_name="burn_action_created_user_id")
    modified_user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,
                                      related_name="burn_action_modified_user_id")
    created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    status = models.IntegerField(default=1)  # 0-inactive, 1-active

    points = models.FloatField(default=0.00)
    terms_and_conditions = models.TextField(null=True)
    image = models.ImageField(upload_to='shop_burns', null=True, blank=True)
    shop = models.ForeignKey(Shop, null=True, blank=True, related_name="burn_coupons")


    def __str__(self):
        return self.name


class EarnTransaction(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name="erned_user_id")
    erned_points = models.FloatField(default=0.00)
    erned_action = models.ForeignKey(EarnActionDetail, models.DO_NOTHING, db_column='action_id',
                                     related_name="erned_user_id")
    validity_date = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    status = models.IntegerField(default=1)  # 0-inactive, 1-active
    is_viewed = models.BooleanField(default=False)


    def __str__(self):
        return str(self.user) + ' - ' + str(self.erned_action)

    class Meta:
        unique_together = (('user', 'erned_action'))


class BurnTransaction(NhanceBaseModel):
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name="burned_user_id")
    burned_points = models.FloatField(default=0.00)
    burned_action = models.ForeignKey(BurnActionDetail, models.DO_NOTHING, blank=True, null=True, db_column='action_id',
                                      related_name="burned_user_id")
    validity_date = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    status = models.IntegerField(default=1)  # 0-inactive, 1-active
    purchased = models.BooleanField(default=True)
    used = models.BooleanField(default=False)


    def __str__(self):
        return str(self.user) + ' - ' + str(self.burned_action)


class EarnBurnTransaction(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name="ern_burn_user_id")
    opening_points = models.FloatField(default=0.00)
    transfer_points = models.FloatField(default=0.00)
    balance_points = models.FloatField(default=0.00)
    transaction_type = models.CharField(choices=TRANSACTION_CHOICES, max_length=5, null=True, blank=True)
    transaction_id = models.IntegerField()  # id of ern/burn trasaction based on transaction_type
    created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    status = models.IntegerField(default=1)  # 0-inactive, 1-active

    def save(self, *args, **kwargs):
        if self.transaction_type == EARN:
            self.balance_points = self.opening_points + self.transfer_points
        else:
            self.balance_points = self.opening_points - self.transfer_points

        super(EarnBurnTransaction, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user) + ' - ' + str(self.transaction_type)


def calculate_balance(earn=None, burn=None):
    return earn - burn


def calculate_earn_amount(earn=None):
    return earn * 1


class Summary(models.Model):
    user = models.OneToOneField(User, models.DO_NOTHING, related_name="earn_burn_summary")
    total_ern_points = models.FloatField(default=0.00)
    total_burn_points = models.FloatField(default=0.00)
    balance_points = models.FloatField(default=0.00)
    expire_points = models.FloatField(blank=True, null=True)
    erned_amount = models.FloatField(default=0.00)
    created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    status = models.IntegerField(default=1)  # 0-inactive, 1-active
    membership = models.ForeignKey(StatusLevel, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.balance_points = calculate_balance(earn=self.total_ern_points, burn=self.total_burn_points)
        self.erned_amount = calculate_earn_amount(self.balance_points)
        super(Summary, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)


class EarnBurnSettings(models.Model):
    ending_days = models.IntegerField()
    name = models.CharField(max_length=255, blank=True, null=True)
    created_user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,
                                     related_name="setting_created_user_id")
    modified_user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,
                                      related_name="setting_modified_user_id")
    created_on = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    status = models.IntegerField(default=1)  # 0-inactive, 1-active

    def __str__(self):
        return self.name


