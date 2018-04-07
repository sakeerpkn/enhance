import pdb
import random
import string

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError, DatabaseError
from django.db.transaction import TransactionManagementError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from django.contrib.auth.models import User, Group
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from api.api_user.models import ProfileDetails
from api.api_user.serializers import UserLoginSerializer
from api.api_zone.models import ZoneToZoneManagerMapping, Shelf
from api.api_zone.serializers import ZoneToZoneManagerMappingSerializer, ZoneToZoneManagerMapSerializer
from .models import CustomerBag, Location, Bag, PhysicalLocation
import datetime
from collections import OrderedDict

def get_process_owners():
    role = Group.objects.get(name='Process_manager')
    process_owners= ProfileDetails.objects.filter(role_id=role)
    return process_owners


def attach_zone_to_process_owner(location,created_user):
    process_owners = get_process_owners()
    for process_owner in process_owners:
        print(process_owner.user_id)
        ZoneToZoneManagerMapping.objects.get_or_create(zone_id=location,manager_id=process_owner.user_id, defaults={'zone_id':location, 'manager_id':process_owner.user_id,'created_user_id':created_user,'modified_user_id':created_user})
    return True


class PhysicalLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalLocation
        fields = ['id', 'name']


# class TransferSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = CustomerBag
#         fields = (
#             'customer_name', 'customer_mobile', 'stored_location_id', 'number_of_bags', 
#             'drop_time', 'shelf','transaction','destination', 'cutomer_type', 'location1',
#             'pick_up_time','location2', 'status')

#     def create(self, validated_data):
#         now = datetime.datetime.now()
#         if 'drop_location' in validated_data:
#             location2 = validated_data['drop_location']
#         else:
#             location2 = None


def generate_shelf_name(size=4, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class BaggageSerializer(serializers.ModelSerializer):
    shelf = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    customer_mobile = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    number_of_bags = serializers.SerializerMethodField()
    drop_time = serializers.SerializerMethodField()

    bag_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomerBag
        fields = (
            'customer_name', 'customer_mobile', 'stored_location_id', 'number_of_bags', 'drop_time', 'shelf',
            'transaction',
            'destination', 'cutomer_type', 'location1', 'pick_up_time'
            , 'location2', 'status','location2','bag_name')

    def get_drop_time(self, obj):
        parent = CustomerBag.objects.get(id=obj.parent_id.id)
        return parent.drop_time

    def get_bag_name(self, obj):
        bag_info = Bag.objects.get(qr_code=obj.stored_location_id)
        return bag_info.name
    

    def get_customer_mobile(self, obj):
        parent = CustomerBag.objects.get(id=obj.parent_id.id)
        return parent.customer_id

    def get_number_of_bags(self, obj):
        parent = CustomerBag.objects.get(id=obj.parent_id.id)
        return parent.number_of_bags

    def get_customer_name(self, obj):
        parent = CustomerBag.objects.get(id=obj.parent_id.id)
        return parent.customer_name


    def get_shelf(self, obj):
        name = None
        if obj.shelf:
            try:
                shelf = Shelf.objects.get(id=obj.shelf)
                name = shelf.name
            except Shelf.DoesNotExist:
                pass
        return name

    def get_destination(self, obj):
        destination = None
        if obj.shelf:
            destination = obj.shelf
            message = "Stored at" + destination

        else:
            profile_details = ProfileDetails.objects.filter(qr_code=obj.location2)
            if profile_details:
                if profile_details[0].user_id.first_name:
                    destination = profile_details[0].user_id.first_name
                else:
                    destination = profile_details[0].user_id.username
            message = "Collected By " + str(destination)

        return message


class LocSerializer(serializers.ModelSerializer):
    current_bags = serializers.SerializerMethodField(read_only=True)
    count_of_managers = serializers.SerializerMethodField(read_only=True)
    managers = ZoneToZoneManagerMapSerializer(many=True)
    physical_location = PhysicalLocationSerializer()

    class Meta:
        model = Location
        fields = (
            'id', 'name', 'category', 'current_bags', 'physical_location', 'capacity_limit', 'total_shelves',
            'managers', 'created_user_id', 'modified_user_id', 'count_of_managers','alias')

    def get_current_bags(self, obj):
        # zone_ids = ZoneToZoneManagerMapping.objects.filter(zone_id=obj.id).values('zone_id__id')
        current_bags = CustomerBag.objects.filter(zone_id=obj, status=0).count()
        return current_bags

    def get_count_of_managers(self, obj):
        return ZoneToZoneManagerMapping.objects.filter(zone_id=obj.id).count()

    @transaction.atomic
    def create(self, validated_data, managers, created_user):
        try:
            pl = get_object_or_404(PhysicalLocation, name=validated_data['physical_location']['name'])
            with transaction.atomic():
                location = Location.objects.create(name=validated_data['name'], category=validated_data['category'],
                                                   physical_location=pl,
                                                   capacity_limit=validated_data['capacity_limit'],
                                                   total_shelves=validated_data['total_shelves'],
                                                   created_user_id=created_user,alias=validated_data['alias'])
                for manager in managers:
                    user = get_object_or_404(User, id=manager['id'])
                    group = get_object_or_404(Group, name='Zone_manager')
                    ProfileDetails.objects.get_or_create(user_id=user, role=group, defaults={
                        'qr_code': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)),
                        'user_id': user, 'role': group})

                    zone_mapping, created = ZoneToZoneManagerMapping.objects.get_or_create(manager_id=user,zone_id=location,
                                                                                           defaults={
                                                                                               'zone_id': location,
                                                                                               'manager_id': user,
                                                                                               'created_user_id': location.created_user_id})
                    if created == 0:
                        zone_mapping.zone_id = location
                        zone_mapping.manager_id = user
                        zone_mapping.created_user_id = location.created_user_id
                        zone_mapping.save()
                for i in range(location.total_shelves):
                    Shelf.objects.create(name=generate_shelf_name(), created_user_id=created_user, zone_id=location)
                attach_zone_to_process_owner(location=location,created_user=location.created_user_id)
                return location
        except PhysicalLocation.DoesNotExist as e:
            raise (e)
        except IntegrityError as e:
            raise (e)
        except DatabaseError as e:
            raise (e)
        except TransactionManagementError as e:
            raise (e)
        except ObjectDoesNotExist as e:
            raise (e)
        except (Group.DoesNotExist, User.DoesNotExist) as e:
            raise (e)

    def update(self, instance, validated_data, modified_user, managers):
        instance.name = validated_data['name']
        instance.category = validated_data['category']
        try:

            with transaction.atomic():
                if instance.physical_location.name != validated_data['physical_location']['name']:
                    pl = get_object_or_404(PhysicalLocation, name=validated_data['physical_location']['name'])
                    instance.physical_location = pl
                instance.capacity_limit = validated_data['capacity_limit']
                old_total_shelves = instance.total_shelves
                instance.total_shelves = validated_data['total_shelves']
                new_total_shelves = validated_data['total_shelves']
                instance.modified_user_id = modified_user
                instance.alias = validated_data['alias']
                instance.save()
                process_owners = ProfileDetails.objects.filter(role__id=1).values_list('user_id',flat=True)
                zone_managers = ZoneToZoneManagerMapping.objects.filter(zone_id=instance).exclude(manager_id_id__in=process_owners)
                zone_managers.delete()
                if old_total_shelves > new_total_shelves:
                    diff = old_total_shelves - new_total_shelves
                    shelves = Shelf.objects.all().order_by('-id')[:diff]
                    for shelf in shelves:
                        shelf.delete()
                elif new_total_shelves > old_total_shelves:
                    diff = new_total_shelves - old_total_shelves
                    for i in range(diff):
                        Shelf.objects.create(name=generate_shelf_name(), zone_id=instance,
                                             created_user_id=modified_user)
                for manager in managers:
                    user = get_object_or_404(User, id=manager['id'])
                    group = get_object_or_404(Group, name='Zone_manager')
                    ProfileDetails.objects.get_or_create(user_id=user, role=group, defaults={
                        'qr_code': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)),
                        'user_id': user, 'role': group})
                    zone_mapping, created = ZoneToZoneManagerMapping.objects.get_or_create(manager_id=user,zone_id=instance,
                                                                                       defaults={
                                                                                           'zone_id': instance,
                                                                                           'manager_id': user,
                                                                                           'created_user_id': instance.created_user_id})
                    if created == 0:
                        zone_mapping.zone_id = instance
                        zone_mapping.manager_id = user
                        zone_mapping.created_user_id = instance.created_user_id
                        zone_mapping.save()
                # attach_zone_to_process_owner(location=instance,created_user=instance.created_user_id)
                return instance

        except PhysicalLocation.DoesNotExist as e:
            raise (e)
        except IntegrityError as e:
            raise (e)
        except DatabaseError as e:
            raise (e)
        except TransactionManagementError as e:
            raise (e)
        except ObjectDoesNotExist as e:
            raise (e)
        except (Group.DoesNotExist, User.DoesNotExist) as e:
            raise (e)


class LocationSerializer(serializers.ModelSerializer):
    current_bags = serializers.SerializerMethodField(read_only=True)
    managers = serializers.ListField(
        child=serializers.CharField(max_length=255), write_only=True
    )
    created_user = serializers.IntegerField(write_only=True)
    modified_user = serializers.IntegerField(write_only=True)
    count_of_managers = serializers.SerializerMethodField(read_only=True)

    def get_current_bags(self, obj):
        zone_ids = ZoneToZoneManagerMapping.objects.filter(zone_id=obj.id).values('zone_id__id')
        current_bags = CustomerBag.objects.filter(location2__in=zone_ids, status=0, transaction=11).count()
        return current_bags

    def get_count_of_managers(self, obj):
        return ZoneToZoneManagerMapping.objects.filter(zone_id=obj.id).count()


    class Meta:
        model = Location
        fields = (
            'id', 'name', 'category', 'current_bags', 'physical_location', 'capacity_limit', 'total_shelves',
            'managers', 'created_user', 'modified_user', 'count_of_managers','alias')


class CustomerHandlerStoreSerializer(serializers.ModelSerializer):

    def validate(self, value):
        if not 'transaction' in value or int(value['transaction']) != 0:
            raise serializers.ValidationError("Transaction value should be correct")
        elif not 'cutomer_type' in value or int(value['cutomer_type']) not in [1, 2]:
            raise serializers.ValidationError("Customer type should be correct")
        elif not 'customer_id' in value or value['customer_id'] == '':
            raise serializers.ValidationError("customer_id should be correct")
        elif not 'stored_location_id' in value or value['stored_location_id'] == '':
            raise serializers.ValidationError("stored_location_id should be correct")
        # elif drop_time in value or value['drop_time'] == '':
        #     raise serializers.ValidationError("drop_time should be correct")
        return value

    class Meta:
        model = CustomerBag
        fields = ('cutomer_type', 'customer_id', 'customer_name',
                  'transaction', 'number_of_bags', 'stored_location_id', 'drop_time')


class HandlerToCustomerDeliverySerializer(serializers.ModelSerializer):

    def validate(self, value):
        if not 'transaction' in value or int(value['transaction']) != 10:
            raise serializers.ValidationError("Transaction value should be correct")
        elif not 'customer_id' in value or value['customer_id'] == '':
            raise serializers.ValidationError("customer_id should be correct")
        # elif not 'stored_location_id' in value or value['stored_location_id'] == '':
        #     raise serializers.ValidationError("stored_location_id should be correct")
        return value

    class Meta:
        model = CustomerBag
        fields = ['transaction', 'customer_id']


class CustomerInitiateDeliverySerializer(serializers.ModelSerializer):
    def validate(self, value):
        if not 'transaction' in value or int(value['transaction']) != 9:
            raise serializers.ValidationError("Transaction value should be correct")
        elif not 'customer_id' in value or value['customer_id'] == '':
            raise serializers.ValidationError("customer_id should be correct")
        # elif not 'stored_location_id' in value or value['stored_location_id'] == '':
        #     raise serializers.ValidationError("stored_location_id should be correct")
        return value

    class Meta:
        model = CustomerBag
        fields = ['transaction', 'customer_id']


class HandlerToHandlerTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBag
        fields = ['transaction']

    def validate_transaction(self, value):
        if int(value) != 1:
            raise serializers.ValidationError("Transaction value should be correct")
        return value


class HandlerToHandlerAcceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBag
        fields = ['transaction']

    def validate_transaction(self, value):
        if int(value) != 2:
            raise serializers.ValidationError("Transaction value should be correct")
        return value


class HandlerToZoneTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBag
        fields = ['transaction']

    def validate_transaction(self, value):
        if int(value) != 3:
            raise serializers.ValidationError("Transaction value should be correct")
        return value


class HandlerToZoneAcceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBag
        fields = ['transaction']

    def validate_transaction(self, value):
        if int(value) != 4:
            raise serializers.ValidationError("Transaction value should be correct")
        return value


class ZoneToHandlerTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBag
        fields = ['transaction']

    def validate_transaction(self, value):
        if int(value) != 5:
            raise serializers.ValidationError("Transaction value should be correct")
        return value


class ZoneToHandlerAcceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBag
        fields = ['transaction']

    def validate_transaction(self, value):
        if int(value) != 6:
            raise serializers.ValidationError("Transaction value should be correct")
        return value


class CustomerToZoneStoreSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        print(validated_data)
        now = datetime.datetime.now()
        if 'drop_location' in validated_data:
            location2 = validated_data['drop_location']
        else:
            location2 = None

        # if 'drop_time' in validated_data:
        #     drop_time = validated_data['drop_time']
        # else:
        #     drop_time = now
        try:
            zone = Location.objects.get(id=int(validated_data['zone_id']), category=1)
        except Exception as e:
            print(e)
            return None

        parent_obj = CustomerBag.objects.create(cutomer_type=validated_data['cutomer_type'],
                                                customer_id=validated_data['customer_id'],
                                                customer_name=validated_data['customer_name'],
                                                number_of_bags=validated_data['number_of_bags'],
                                                stored_location_id=validated_data['stored_location_id'],
                                                drop_time=validated_data['drop_time'],
                                                transaction=0, location1=validated_data['zone_manager_qr_code'],
                                                pick_up_time=now, location2=location2, status=0)
        child_obj = CustomerBag.objects.create(cutomer_type=validated_data['cutomer_type'],
                                               customer_id=validated_data['customer_id'],
                                               customer_name=validated_data['customer_name'],
                                               number_of_bags=validated_data['number_of_bags'],
                                               stored_location_id=validated_data['stored_location_id'],
                                               drop_time=validated_data['drop_time'],
                                               location1=validated_data['customer_id'], pick_up_time=now,
                                               location2=validated_data['zone_manager_qr_code'], status=0, zone=zone,
                                               parent_id=parent_obj, transaction=7)

        print("child obj", child_obj)
        return child_obj

    zone_manager_qr_code = serializers.CharField(write_only=True)
    zone_id = serializers.IntegerField()
    drop_location = serializers.CharField(required=False, allow_blank=True)

    # drop_time = serializers.DateTimeField(required=False)
    class Meta:
        model = CustomerBag
        fields = ('cutomer_type', 'customer_id', 'customer_name',
                  'transaction', 'number_of_bags', 'stored_location_id', 'drop_time', 'zone_manager_qr_code',
                  'drop_location', 'zone_id')


class ZoneToCustomerDeliverySerializer(serializers.ModelSerializer):
    def validate(self, value):
        if not 'transaction' in value or int(value['transaction']) != 8:
            raise serializers.ValidationError("Transaction value should be correct")
        elif not 'customer_id' in value or value['customer_id'] == '':
            raise serializers.ValidationError("customer_id should be correct")
        # elif not 'stored_location_id' in value or value['stored_location_id'] == '':
        #     raise serializers.ValidationError("stored_location_id should be correct")
        return value

    class Meta:
        model = CustomerBag
        fields = ['transaction', 'customer_id']


class BagDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bag
        fields = ['qr_code']
        # fields = '__all__'


class BaggageDetailsSerializer(serializers.ModelSerializer):
    qr_code = serializers.CharField(read_only=True)

    class Meta:
        model = Bag
        fields = ('id', 'name', 'status', 'qr_code', 'created_user_id', 'modified_user_id')


class BaggageListSerializer(serializers.ModelSerializer):
    qr_code = serializers.CharField(read_only=True)

    class Meta:
        model = Bag
        fields = ('name', 'qr_code')


class BagHistorySerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()
    time = serializers.DateTimeField(source='created_on')

    class Meta:
        model = CustomerBag
        fields = ['time', 'message', 'id']

    def get_message(self, obj):
        try:
            profile_obj = ProfileDetails.objects.filter(qr_code=obj.location2).first()
            if profile_obj.user_id.first_name:
                return 'Handed over to ' + str(profile_obj.user_id.first_name)
            else:
                return 'Handed over to ' + str(profile_obj.user_id.username)

        except ProfileDetails.DoesNotExist:
            pass
        return None


class ViewAllBagSerializer(serializers.ModelSerializer):

    customer_mobile = serializers.CharField(source='customer_id')
    class Meta:
        model = CustomerBag
        fields = ('cutomer_type', 'customer_mobile', 'customer_name',
                  'transaction', 'number_of_bags', 'stored_location_id', 'drop_time','customer_requested_place','customer_requested_time','customer_requested')