from django.contrib.auth.models import User
from django.db.models import Q
from django_filters import rest_framework as filters

from api.api_user.models import ProfileDetails
from api.api_zone.models import ZoneToZoneManagerMapping, Shelf
from .models import Location, CustomerBag, Bag


def get_managers():
    user_ids = ProfileDetails.objects.filter(role__id=2).values('user_id__id')

    return User.objects.filter(id__in=user_ids)

def get_managers_based_zone_id(zone_id):
    return ZoneToZoneManagerMapping.objects.filter(zone_id=zone_id).values_list('manager_id', flat=True).distinct()

def get_username_from_id_list(user_id_list):
    return User.objects.filter(id__in=user_id_list)
class ZoneFilter(filters.FilterSet):
    manager = filters.CharFilter(
        label='Zone Manager', method='get_my_zones'
    )
    name = filters.CharFilter(name="name", method='custom_name_filter')
    physical_location = filters.CharFilter(method='custom_location_filter'
                                           )

    class Meta:
        model = Location
        fields = ['physical_location', 'name']

    def custom_name_filter(self, queryset, name, value):
        return queryset.filter(name__icontains=value, category=1)

    def get_my_zones(self, queryset, name, value):
        zone_ids = ZoneToZoneManagerMapping.objects.filter(Q(manager_id__username__icontains=value)| Q(manager_id__first_name__icontains=value)).values('zone_id__id')
        return queryset.filter(id__in=zone_ids)

    def custom_location_filter(self, queryset, name, value):
        return queryset.filter(physical_location__name__icontains=value, category=1)


def UTC_to_IST_time(utc):
    try:
        from pytz import timezone
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        loc_dt = utc.astimezone(timezone('Asia/Kolkata'))
        return loc_dt.strftime(fmt)
    except Exception as e:
        print(e)
        return utc

def get_profile_first_name_frm_qr_code(qr_code):
    profile_obj = ProfileDetails.objects.filter(qr_code=qr_code).first()
    if profile_obj and profile_obj.user_id.first_name:
        return profile_obj.user_id.first_name
    elif profile_obj and profile_obj.user_id.username:
        return profile_obj.user_id.username
    else:
        return qr_code

def get_action_time(child):
    if child.customer_requested and child.customer_requested != '' and child.customer_requested != None:
        return UTC_to_IST_time(child.customer_requested_time)
    else:
        return UTC_to_IST_time(child.created_on)

def get_action_message(origin_user_name,dest_user_name,child):
    message = ''
    if child.customer_requested and child.customer_requested != '' and child.customer_requested != None:
        message = 'Customer requested: Bag is with  ' + dest_user_name +' for delivery at ' + str(child.customer_requested_place.name)
    else:
        message = 'Bag is with ' + dest_user_name
    return message

def get_shelf_action_message(child):
    shelf_obj = Shelf.objects.get(id=child.shelf)
    message = ''
    if child.customer_requested and child.customer_requested != '' and child.customer_requested != None:
        message = 'Customer requested: Stored at ' + str(shelf_obj.name) +' for delivery at ' + str(child.customer_requested_place.name)
    else:
        message = 'Stored at ' + str(shelf_obj.name)
    return message


def get_bag_info_by_qrcode(qrcode):
    return Bag.objects.get(qr_code=qrcode)
    
def get_bag_info_by_bag_name(bag_name):
    return Bag.objects.filter(name__startswith=bag_name).values_list('qr_code')

def get_the_initial_receiver_by_parent_id(parent_id):
    try:
        child = CustomerBag.objects.filter(parent_id=parent_id).order_by('id').first()
        if child and child != None:
            return get_profile_first_name_frm_qr_code(child.location2)
        else:
            return 'Not found'
    except Exception as e:
        print ("there is exception get_the_initial_receiver_by_parent_id", e)
        return 'Not found'
