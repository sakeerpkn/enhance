from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from api.api_baggage.models import CustomerBag, Bag, Location
from api.api_user.models import ProfileDetails
from .models import Shelf, ZoneToZoneManagerMapping
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from django.db import connection
from rest_framework import mixins, generics, viewsets
from django.contrib.auth import authenticate
from .serializers import ZoneSerializer, ShelfSerializer, ZonerToShelfTransferSerializer, BagInfoSerializer

import json
import datetime
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.db.models import Q

from django_filters.rest_framework import DjangoFilterBackend

from api.api_baggage.api_global_modules import transaction_update_create, send_message
from api.api_baggage.filter import get_bag_info_by_bag_name, get_the_initial_receiver_by_parent_id



# Create your views here.

class ListRetrieveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class CreateViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class UpdateViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class BaggageViewSet(ListRetrieveViewSet):
    """
    Description: This class is used to get the baggage status
    Author : Sakeer P
    Created At : 26th Feb 2018
    """
    queryset = CustomerBag.objects.all()
    serializer_class = BagInfoSerializer



class ZoneBaggageViewSet(ListRetrieveViewSet):
    """
    Description: This class is used to get the baggage status 
    """
    queryset = CustomerBag.objects.all()
    serializer_class = ZoneSerializer
    
    
    def list(self, request, *args, **kwargs):
        try:
            self.response = {}
            self.response['result'] = []
            zone_ids = self.request.query_params.get('zones', None)

            customer_name = self.request.query_params.get('customer_name', None)
            customer_mobile = self.request.query_params.get('customer_mobile', None)

            # ACTUALLY WE ARE ACCEPTIIN NAME HERE
            baggage_code = self.request.query_params.get('baggage_code', None)
            role_id = self.request.query_params.get('role_id', None)
            limit = self.request.query_params.get('limit', 9)
            offset = self.request.query_params.get('offset', 0)

            if zone_ids and role_id is not None:
                print ("zone idssssssssssssssss",zone_ids)
                zone_ids = [x.strip() for x in zone_ids.split(',')]
                print ("after split", zone_ids)
                customer_bag_info = CustomerBag.objects.filter(Q(zone_id__in=zone_ids),
                                                               Q(status=0), Q(transaction__in=[2, 4, 6, 9, 7, 11])).exclude(
                    parent_id=None).order_by('-created_on')
            else:
                customer_bag_info = CustomerBag.objects.filter(status=0).exclude(parent_id=None).order_by('-created_on')
            if role_id and role_id is not None:
                role_id = [x.strip() for x in role_id.split(',')]
                print ("roles===========", role_id)
                if '1' in role_id:
                    print ("it is process owner")
                    customer_bag_info = CustomerBag.objects.filter(status=0).exclude(parent_id=None).order_by('-created_on')

            if (customer_name and customer_name is not None):
                print ("customer_name=====", customer_name)
                customer_bag_info = customer_bag_info.filter(parent_id__customer_name__icontains=customer_name)
            if (customer_mobile and customer_mobile is not None):
                print ("mobile number search==", customer_mobile)
                customer_bag_info = customer_bag_info.filter(parent_id__customer_id__startswith=customer_mobile)

            if (baggage_code and baggage_code is not None):
                try:
                    baggage_code = baggage_code.upper()
                    bag_detail_info = get_bag_info_by_bag_name(baggage_code)
                    customer_bag_info = customer_bag_info.filter(stored_location_id__in=bag_detail_info)
                except Exception as e:
                    print ("passed", e)
                    pass
            customer_bag_info = customer_bag_info[int(offset):int(limit)]
            if customer_bag_info:
                for bag_info in customer_bag_info:
                    print ("bag info====",bag_info.id)
                    destination_name = ''
                    self.bag_dict = {}
                    parent_id = bag_info.parent_id
                    self.bag_dict['customer_name'] = parent_id.customer_name
                    self.bag_dict['customer_mobile'] = parent_id.customer_id
                    baggage_data = Bag.objects.get(qr_code=bag_info.stored_location_id)
                    self.bag_dict['baggage'] = baggage_data.name
                    self.bag_dict['baggage_code'] = baggage_data.qr_code

                    if bag_info.customer_requested and bag_info.customer_requested == 1:
                        self.bag_dict['destination'] = 'Customer'
                    elif bag_info.customer_requested != 1 and bag_info.zone :
                        self.bag_dict['destination'] = '-'
                    elif bag_info.customer_requested != 1 and (bag_info.zone == None or bag_info.zone == ''):
                        self.bag_dict['destination'] = 'Zone'
                    else:
                        self.bag_dict['destination'] = '-'

                    self.bag_dict['initial_receiver'] = get_the_initial_receiver_by_parent_id(bag_info.parent_id)


                    if bag_info.shelf:
                        shelf_data = Shelf.objects.get(id=bag_info.shelf)
                        self.bag_dict['shelf'] = shelf_data.name
                    else:
                        self.bag_dict['shelf'] = "NA"

                    if bag_info.zone:
                        # zone_data = Location.objects.get(id=bag_info.zone)
                        self.bag_dict['zone'] = bag_info.zone.id
                    else:
                        self.bag_dict['zone'] = "NA"

                    if bag_info.location2 != '':
                        try:
                            print ("bag transaction==", bag_info.transaction, "bag name==", bag_info.customer_name)
                            if bag_info.transaction == '11':
                                profile_obj = ProfileDetails.objects.filter(qr_code=bag_info.location1).last()
                            else:
                                profile_obj = ProfileDetails.objects.filter(qr_code=bag_info.location2).last()
                            if profile_obj.user_id.first_name:
                                destination_name = profile_obj.user_id.first_name
                            else:
                                destination_name = profile_obj.user_id.username
                            self.bag_dict['handler_number'] = profile_obj.user_id.username
                            if bag_info.transaction == "0" or bag_info.transaction == "2":
                                self.bag_dict['status_message'] = "Bag with " + destination_name
                                if profile_obj.role.id == 3:
                                    self.bag_dict['status_code'] = 1
                                elif profile_obj.role.id == 2:
                                    self.bag_dict['status_code'] = 2
                                else:
                                    pass
                        except Exception as e:
                            print("Exception while getting the profile info, its passed", e)

                        self.bag_dict['transaction'] = bag_info.transaction

                        if bag_info.transaction == "4" or bag_info.transaction == "7" :
                            self.bag_dict['status_message'] = "Bag at zone "
                            self.bag_dict['status_code'] = 2
                        if bag_info.transaction == "11":
                            self.bag_dict['status_message'] = "Bag at " + self.bag_dict['shelf']
                            self.bag_dict['status_code'] = 3
                        if bag_info.transaction == "6":
                            self.bag_dict['status_message'] = "Bag is with " + destination_name 
                            self.bag_dict['status_code'] = 11

                        if bag_info.customer_requested == 1 :
                            print ("destination_name====", destination_name)
                            self.bag_dict['status_message'] = "Bag with " + destination_name + " for delivery at " + bag_info.customer_requested_place.name
                            if bag_info.transaction == "11":
                                print ("self.bag_dict['shelf']", self.bag_dict['shelf'])
                                self.bag_dict['status_message'] = "Bag is at " + self.bag_dict['shelf'] + " for delivery at " + bag_info.customer_requested_place.name
                            self.bag_dict['status_code'] = 4

                        self.response['result'].append(self.bag_dict)
                
            else:
                self.bag_dict = {}
                self.response['result'] = []
        except Exception as e:
            print("Exception in bag info", e)
        self.response['status'] = 200
        return Response(self.response)


class ZoneShelf(ListRetrieveViewSet):
    """
    Description: This class is used to list zone wise details

    """
    queryset = Shelf.objects.filter(status=1)
    serializer_class = ShelfSerializer

    def list(self, request, *args, **kwargs):
        self.response = {}
        self.response['result'] = []
        zone_id = self.request.query_params.get('zone_id', None)
        if zone_id and zone_id is not None:
            print ("zone id", zone_id)
            zoneshelf = self.queryset.filter(zone_id=zone_id)
            print (self.queryset.filter(zone_id__in=zone_id).query)
            print("zoneshelf", zoneshelf)
            for shelf in zoneshelf:
                print("shelf id==", shelf.id)
                temp_dict = {}
                shelfBagCount = CustomerBag.objects.filter(shelf=shelf.id, status=0).count()
                print("shelfBagCount==", shelfBagCount)
                temp_dict['id'] = shelf.id
                temp_dict['shelf'] = shelf.name
                temp_dict['shelf_bag_count'] = shelfBagCount
                self.response['result'].append(temp_dict)
                self.response['status'] = 200
            return Response(self.response)
        else:
            self.queryset = []
            return Response(self.response)


class ZonerToShelfTransferCreateSet(CreateViewSet):
    """
    Description: This class is used to transfer a bag to shelf from zoner

    """
    queryset = CustomerBag.objects.all()
    serializer_class = ZonerToShelfTransferSerializer

    def create(self, request, *args, **kwargs):
        self.response = {}
        self.response['result'] = []
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            self.response['status'] = 200
            self.response['message'] = 'These bags are transfered to the shelf'
        return Response(self.response)

    # return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    def perform_create(self, serializer):
        now = datetime.datetime.now()
        location1 = self.request.data.get('zone_manager_qr_code', None)
        # zoner_manager_code = self.request.data.get('zoner_manager_code', None)

        baggage_code = self.request.data.get('baggage_code', None)
        location2 = self.request.data.get('shelf_id', None)
        zone_id = self.request.data.get('zone_id', None)
        print("baggage codes===", baggage_code)
        parent_obj = {}
        transaction = self.request.data.get('transaction', 11)
        try:
            zone = Location.objects.get(id=int(zone_id), category=1)
            print("zone object", zone)
            for bag_id in baggage_code:
                print("bag id==", bag_id)
                try:
                    parent_obj = CustomerBag.objects.filter(status=0, stored_location_id=bag_id, transaction=0,
                                                            parent_id=None).last()
                    print("parent_obj====", parent_obj)
                except Exception as e:
                    print("Exception", e)
                if parent_obj:
                    child_obj = CustomerBag.objects.filter(stored_location_id=bag_id, status=0, parent_id=parent_obj)
                    print("child=====", child_obj)
                    transaction_update_create(parent_obj, child_obj, bag_id, transaction, location1, location2, zone
                                          )
                    self.response['result'].append(bag_id)
        except Exception as e:
            self.response['result'] = []
            print("exception===", e)
            pass
