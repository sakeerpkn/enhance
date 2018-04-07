from rest_framework import serializers
from api.api_baggage.models import CustomerBag
from api.api_user.serializers import UserLoginSerializer
from .models import Shelf, ZoneToZoneManagerMapping




class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBag
        # fields = '__all__'
        fields = (
            'customer_id', 'customer_name', 'baggage', 'destination', 'shelf', 'status_message', 'status_code',
            'location2')


class BagInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBag
        # fields = '__all__'
        fields = (
            'customer_id', 'customer_name',  'shelf',
            'location2')


class ShelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelf
        # fields = '__all__'
        fields = ('id', 'name')


class ZonerToShelfTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBag
        fields = ['transaction']

    def validate_transaction(self, value):
        if int(value) != 11:
            raise serializers.ValidationError("Transaction value should be correct")
        return value


class ZoneToZoneManagerMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZoneToZoneManagerMapping
        fields = ['id', ]


class ZoneToZoneManagerMapSerializer(serializers.ModelSerializer):
    user = UserLoginSerializer(source='manager_id',read_only=True)

    class Meta:
        model = ZoneToZoneManagerMapping
        fields = ['user']
