from datetime import datetime, timedelta

from django.contrib.auth.models import User, Group
from django.db import transaction
from rest_framework import serializers
from rest_framework.response import Response

from api.api_baggage.models import create_qrcode
from api.api_ern_burn.models import EarnActionDetail, BurnActionDetail, EarnTransaction, DATE, BurnTransaction, Summary
# from api.api_user.serializers import ProfileUserSerializer
from api.api_user.models import ProfileDetails, CustomerDetail, AddressForUser
from api.api_user.serializers import CustomerProfileUserSerializer, CustomerAddressSerializer
from base_app.models import Shop, StatusLevel, ShopStatus, NhanceDocuments
from base_app.serializers import BaseShopCategorySerializer, StatusLevelSerializer
from customer.models import ImageGallery, CustomerInvite
from newsfeed.models import NewsFeed, NewsFeedUserLike
from customer.models import CustomerQueryType
from api.api_user.models import CustomerDetail, ProfileDetails
from django.contrib.auth.models import User


# from api.api_user.serializers import CustomerUserSerializer

class ImageGalleryShortSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ImageGallery
        fields = ['image', 'title', 'tag']

    def get_image(self, obj):
        try:
            return obj.image.url
        except:
            return None


class ShopShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name"]


class EarnActionDetailSerializer(serializers.ModelSerializer):
    shop = ShopShortSerializer()
    image = serializers.SerializerMethodField()

    class Meta:
        model = EarnActionDetail
        exclude = ['created_on', 'modified_on', 'created_user', 'modified_user']

    def get_image(self, obj):
        try:
            return obj.image.url
        except:
            return None


class ShopSerializer(serializers.ModelSerializer):
    category = BaseShopCategorySerializer(many=True)
    no_of_coupons = serializers.SerializerMethodField(read_only=True)
    earn_coupons = EarnActionDetailSerializer(many=True)
    first_letter = serializers.SerializerMethodField(read_only=True)

    multiplex_value = serializers.SerializerMethodField(read_only=True)
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ["id", "name", "floor_number", "contact_number", "status", "shop_number", "no_of_coupons",
                  "description", "logo", "category", "earn_coupons", "first_letter", "multiplex_value"]

    def get_no_of_coupons(self, obj):
        return obj.earn_coupons.count()

    def get_first_letter(self, obj):
        return obj.name[0]

    def get_multiplex_value(self, obj):
        # user = None
        request = self.context.get("request")
        # if request and hasattr(request, "user"):
        #     user = request.user
        #     return 0
        #

        try:
            summary = Summary.objects.get(user=request.user)
        except:
            try:
                shop_status = ShopStatus.objects.get(shop=obj, status_card_level__points_needed=0.0)
                return shop_status.multiplied_by
            except:
                return 0

        try:
            shop_status = ShopStatus.objects.get(shop=obj, status_card_level=summary.membership)
            return shop_status.multiplied_by
        except:
            return 0

    def get_logo(self, obj):
        try:
            return obj.logo.url
        except:
            return None


class BurnActionDetailSerializer(serializers.ModelSerializer):
    shop = ShopShortSerializer()
    image = serializers.SerializerMethodField()

    class Meta:
        model = BurnActionDetail
        exclude = ['created_on', 'modified_on', 'created_user', 'modified_user']

    def get_image(self, obj):
        try:
            return obj.image.url
        except:
            return None


class EarnTransactionSerializer(serializers.ModelSerializer):
    validity_date = serializers.DateTimeField(read_only=True)
    erned_action = serializers.SerializerMethodField()

    class Meta:
        model = EarnTransaction
        fields = ('erned_points', 'erned_action', 'validity_date')

    def create(self, validated_data, user=None, earned_action=None):
        instance = EarnTransaction.objects.create(**validated_data, user=user, erned_action=earned_action)
        if instance.erned_action.validity_type == DATE:
            instance.validity_date = instance.erned_action.validity_date
        else:
            instance.validity_date = datetime.now() + timedelta(days=instance.erned_action.validity_days)
        instance.save()
        return instance

    def get_erned_action(self, obj):
        try:
            return str(obj.erned_action.name)
        except:
            return ""


class BurnTransactionSerializer(serializers.ModelSerializer):
    validity_date = serializers.DateTimeField(read_only=True)
    burned_action = serializers.SerializerMethodField()
    redeeming_date = serializers.DateTimeField(source='created_at')


    class Meta:
        model = BurnTransaction
        fields = ('id','burned_points', 'validity_date','redeeming_date','burned_action',)


    def create(self, validated_data, user=None, burned_action=burned_action):
        instance = BurnTransaction.objects.create(**validated_data, user=user, burned_action=burned_action)
        if instance.burned_action.validity_type == DATE:
            instance.validity_date = instance.burned_action.validity_date
        else:
            instance.validity_date = datetime.now() + timedelta(days=instance.burned_action.validity_days)
        instance.save()
        return instance

    def get_burned_action(self, obj):
        try:
            return str(obj.burned_action.name)
        except:
            return ""


class SummarySerializer(serializers.ModelSerializer):
    current_membership = StatusLevelSerializer(source='membership')
    next_membership = serializers.SerializerMethodField(read_only=True)
    rank = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Summary
        fields = ['total_ern_points', 'total_burn_points', 'balance_points', 'expire_points', 'erned_amount',
                  'current_membership', 'next_membership', 'rank']

    def get_next_membership(self, obj):
        try:
            next_level = StatusLevel.objects.get(priority=obj.membership.priority + 1)
            serializer = StatusLevelSerializer(next_level)
            return serializer.data
        except StatusLevel.DoesNotExist:
            return None

    def get_rank(self, obj):
        summary = Summary.objects.all().order_by('-balance_points').values('user', 'balance_points')
        rank = list(summary).index({'user': obj.user.id, 'balance_points': obj.balance_points})
        return (rank + 1)


class NewsFeedSerializer(serializers.ModelSerializer):
    images = ImageGalleryShortSerializer(many=True)
    liked = serializers.SerializerMethodField()
    attending = serializers.SerializerMethodField()

    class Meta:
        model = NewsFeed
        exclude = ['created_by', 'modified_by', 'updated_at']

    def get_liked(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            try:
                NewsFeedUserLike.objects.get(news_feed=obj, user=user, status=1)
                return True
            except:
                return False
        return False

    def get_attending(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            try:
                NewsFeedUserLike.objects.get(news_feed=obj, user=user, attending=1)
                return True
            except:
                return False
        return False


class CustomerQueryTypeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerQueryType
        fields = ['id', 'title', 'description']

    def get_attending(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            try:
                NewsFeedUserLike.objects.get(news_feed=obj, user=user, attending=1)
                return True
            except:
                return False
        return False


# imprt
class CustomerDetailSerializer(serializers.ModelSerializer):
    # def validate_empty_values(self, data):
    #     if data['date_of_birth']=="":
    #         data['date_of_birth'] = None
    #     return data

    # def validate(self, data):
    #     if data['date_of_birth']=="":
    #         data['date_of_birth'] = None
    #     return data
    date_of_birth = serializers.DateField(read_only=True)

    class Meta:
        model = CustomerDetail
        fields = ['profession', 'favourite_shop', 'date_of_birth', 'gender', 'address']


# imprt end


class CustomerProfileSerializer(serializers.Serializer):
    user = CustomerProfileUserSerializer()
    profile = CustomerDetailSerializer()


# start
class CustomerUserSerializer(serializers.ModelSerializer):
    user_address = CustomerAddressSerializer()
    earn_burn_summary = SummarySerializer(read_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email', 'user_address', 'earn_burn_summary']


class ProfileDetailSerializer(serializers.ModelSerializer):
    user_details = CustomerUserSerializer(source='user_id')

    class Meta:
        model = ProfileDetails
        fields = ['user_details', 'role']


class CustomerSerializer(serializers.Serializer):
    user = CustomerUserSerializer()
    address = CustomerAddressSerializer(required=False)
    customer = CustomerDetailSerializer()

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['user']['username'], email=validated_data['user']['email'],
                                   first_name=validated_data['user']['first_name'])
        role, created = Group.objects.get_or_create(name='customer', defaults={'name': 'customer'})

        profile_detail = ProfileDetails.objects.create(user_id=user, role=role, qr_code=create_qrcode())
        if validated_data['address']:
            AddressForUser.objects.create(user=user, addressline1=validated_data['address']['addressline1'],
                                          addressline2=validated_data['address']['addressline2'],
                                          area=validated_data['address']['area'],
                                          zipcode=validated_data['address']['zipcode'],
                                          country=validated_data['address']['country'],
                                          state=validated_data['address']['state'],
                                          city=validated_data['address']['city'])

        CustomerDetail.objects.create(profession=validated_data['customer']['profession'],
                                      date_of_birth=validated_data['customer']['date_of_birth'], user=profile_detail,
                                      favourite_shop=validated_data['customer']['favourite_shop'],
                                      gender=validated_data['customer']['gender'])

        return validated_data

    def update(self, instance, validated_data):
        user = instance.create(username=validated_data['user']['username'], email=validated_data['user']['email'],
                               first_name=validated_data['user']['first_name'])
        if validated_data['address']:
            address, created = AddressForUser.get_or_create(user=user)

            if not created:
                address.update(addressline1=validated_data['address']['addressline1'],
                               addressline2=validated_data['address']['addressline2'],
                               area=validated_data['address']['area'],
                               zipcode=validated_data['address']['zipcode'],
                               country=validated_data['address']['country'],
                               state=validated_data['address']['state'],
                               city=validated_data['address']['city'])
        try:
            profile_detail = ProfileDetails.objects.filter(user_id=user).first()

            CustomerDetail.objects.filter(user=profile_detail).update(
                profession=validated_data['customer']['profession'],
                date_of_birth=validated_data['customer']['date_of_birth'],
                favourite_shop=validated_data['customer']['favourite_shop'],
                gender=validated_data['customer']['gender'])
        except ProfileDetails.DoesNotExist:
            pass

        return validated_data


# class CustomerEditSerializer(serializers.Serializer):
#     profile = CustomerProfileSerializer()


class CustomCustomerSerializer(serializers.ModelSerializer):
    profile = ProfileDetailSerializer(source='user')
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomerDetail
        fields = ['id', 'profession', 'favourite_shop', 'date_of_birth', 'gender', 'profile', 'address']

    def create(self, validated_data):
        profile = validated_data['user']
        user = profile['user_id']
        with transaction.atomic():
            user_obj = User.objects.create(username=user['username'], first_name=user['first_name'],
                                           email=user['email'])
            profile_obj = ProfileDetails.objects.create(qr_code=create_qrcode(), user_id=user_obj, role=profile['role'])

            user_address = user['user_address']
            AddressForUser.objects.create(user=user_obj, addressline1=user_address['addressline1'],
                                          addressline2=user_address['addressline2'], area=user_address['area'],
                                          zipcode=user_address['zipcode'], country=user_address['country'],
                                          state=user_address['state'], city=user_address['city'])
            CustomerDetail.objects.create(user=profile_obj, profession=validated_data['profession'],
                                          favourite_shop=validated_data['favourite_shop'],
                                          date_of_birth=validated_data['date_of_birth'],
                                          gender=validated_data['gender'])
            return validated_data


class CustomerInviteShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerInvite
        fields = ['mobile_number']
        
class NhanceDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NhanceDocuments
        fields = ['content']


class ShopLimitedSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name", ]

class BurnTransactionDetailSerializer(serializers.ModelSerializer):
    validity_date = serializers.DateTimeField(read_only=True)
    burned_action = BurnActionDetailSerializer()
    redeeming_date = serializers.DateTimeField(source='created_at')

    class Meta:
        model = BurnTransaction
        fields = ('id','burned_points', 'validity_date','redeeming_date','burned_action',)
