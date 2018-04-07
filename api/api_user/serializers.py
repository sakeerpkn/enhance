from rest_framework import serializers

from django.contrib.auth.models import User

from .models import ProfileDetails, AddressForUser
from .models import UserOTP


class UserOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOTP
        fields = ['mobile_number']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_name', 'id', 'user_mobile,user_type')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'id', 'first_name']


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'id', 'first_name']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileDetails
        fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'password', 'is_staff']


class CustomerAddressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = AddressForUser
        fields = ['id', 'addressline1', 'addressline2', 'area', 'zipcode', 'country', 'state', 'city']


class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'email']


class CustomerProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','email']



class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','first_name','email']