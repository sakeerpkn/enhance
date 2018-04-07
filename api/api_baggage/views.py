from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.views import APIView
from enhance.constants import CUSTOMER_REQ, CUSTOMER_RECEIVE, HANDLER_TRANSFER,HANDLER_RECIEVER,ZONE_TRANSFER,ZONE_RECIEVER
from api.api_baggage.apps import generate_username, get_qr
from .models import CustomerBag, Location, Bag, PhysicalLocation
from api.api_user.models import ProfileDetails
from api.api_zone.models import Shelf
from rest_framework.decorators import api_view
from rest_framework import mixins, generics, viewsets
from .serializers import BaggageSerializer, HandlerToCustomerDeliverySerializer, \
    CustomerInitiateDeliverySerializer, \
    CustomerHandlerStoreSerializer, \
    HandlerToHandlerTransferSerializer, \
    HandlerToHandlerAcceptSerializer, \
    HandlerToZoneTransferSerializer, \
    HandlerToZoneAcceptSerializer, \
    ZoneToHandlerTransferSerializer, \
    ZoneToHandlerAcceptSerializer, \
    CustomerToZoneStoreSerializer, \
    ZoneToCustomerDeliverySerializer, \
    LocationSerializer, \
    BagDetailsSerializer, PhysicalLocationSerializer, BagHistorySerializer, ViewAllBagSerializer

from rest_framework.decorators import detail_route, list_route
import json
import datetime
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from django.db import connection
from fcm.utils import get_device_model
from .api_global_modules import transaction_update_create, send_message
from .filter import UTC_to_IST_time, get_profile_first_name_frm_qr_code, \
    get_action_time, get_action_message,get_shelf_action_message, get_managers_based_zone_id,get_username_from_id_list,\
    get_bag_info_by_qrcode

class ListRetrieveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class CreateViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass

# def tes(request):
#     group_obj = Group.objects.get(name="Handler")
#
#     for i in range(10):
#         user = User(username=generate_username(), password='pass@123', first_name="handler_" + str(i + 1))
#         user.set_password('pass@123@')
#         user.save()
#         p = ProfileDetails.objects.create(user_id=user, qr_code=get_qr(), role=group_obj)
#         Bag.objects.create(qr_code=p.qr_code, name=user.first_name)
#     pass

class WhereIsMyTamperBag(generics.ListAPIView):

    def get_queryset(self):


        if self.request.query_params.get(' handler_qr_code') and self.request.query_params.get('customer_id'):
            return CustomerBag.objects.filter(location2=self.request.query_params.get(' handler_qr_code'),
                                              customer_id=self.request.query_params.get('customer_id', None), status=0)

        elif self.request.query_params.get(' handler_qr_code'):
            return CustomerBag.objects.filter(location2=self.request.query_params.get(' handler_qr_code'), status=0)

        elif self.request.query_params.get('customer_id'):
            custom_dict = []
            custom_dict.append(CustomerBag.objects.filter(
                customer_id=self.request.query_params.get('customer_id', None),
                status=0).last())
            return custom_dict

    serializer_class = BaggageSerializer





class CustomerBagViewSet(ListRetrieveViewSet):
    queryset = CustomerBag.objects.all()
    serializer_class = BaggageSerializer

    def list(self, request, *args, **kwargs):
        bag_info = []
        self.response = []
        handler_id = self.request.query_params.get('handler_qr_code', None)
        customer_id = self.request.query_params.get('customer_id', None)
        if customer_id and handler_id and customer_id is not None and handler_id is not None:
            print("search based on customer_id and handler_id============", customer_id, handler_id)
            # queryset = self.queryset.filter(customer_id=customer_id, status=0).exclude(parent_id__isnull=True)
            queryset = self.queryset.filter(location2=handler_id, status=0, parent_id__isnull=False)
            print("queryset", queryset)
            for bag in queryset:
                temp_dict = {}
                if bag.parent_id != None:
                    bag = bag.parent_id
                if bag.customer_id == customer_id:
                    temp_dict['customer_name'] = bag.customer_name
                    temp_dict['customer_mobile'] = bag.customer_id
                    temp_dict['stored_location_id'] = bag.stored_location_id
                    try:
                        bag_info_detail = get_bag_info_by_qrcode(bag.stored_location_id)
                        if bag_info_detail:
                            temp_dict['bag_name'] = bag_info_detail.name
                    except Exception as e:
                        print ("get bag info exception", e)

                    temp_dict['number_of_bags'] = bag.number_of_bags
                    # drop_time = UTC_to_IST_time(bag.drop_time)
                    # temp_dict['drop_time'] = bag.drop_time
                    temp_dict['drop_time'] = bag.drop_time
                    temp_dict['transaction'] = bag.transaction
                    temp_dict['shelf'] = bag.shelf
                    # temp_dict['location2'] = bag.location2

                    try:
                        child_objects = CustomerBag.objects.filter(parent_id=bag.id).order_by('created_on')
                        for child in child_objects:
                            try:
                                if child.zone:
                                    profile_obj = ProfileDetails.objects.filter(id=child.location2).first()
                                else:
                                    profile_obj = ProfileDetails.objects.filter(qr_code=child.location2).first()
                                if profile_obj.user_id.first_name:
                                    temp_dict['destination'] = 'Collected by ' + str(profile_obj.user_id.first_name)
                                else:
                                    temp_dict['destination'] = 'Collected by ' + str(profile_obj.user_id.username)
                            except ProfileDetails.DoesNotExist:
                                print("profile not available for qr code", child.location2)
                                pass

                            if child.shelf and child.shelf != '':
                                print("Stored at zone", child.shelf)
                                try:
                                    shelf_obj = Shelf.objects.get(id=child.shelf)
                                    destination_str = 'Stored at ' + str(shelf_obj.zone_id.name)
                                    if shelf_obj.zone_id.alias:
                                        destination_str += "(" + shelf_obj.zone_id.alias + ")"

                                    temp_dict['destination'] = destination_str

                                    temp_dict['shelf'] = child.shelf
                                except shelf_obj.DoesNotExist:
                                    print("shelf not available")
                                    pass
                            else:
                                pass
                    except Exception as e:
                        print("Exception while getting the child info", e)
                        pass
                    self.response.append(temp_dict)
            return Response(self.response, status=200)

        elif customer_id and customer_id is not None:
            print("search based on customer_id ==========", customer_id)
            # queryset = self.queryset.filter(customer_id=customer_id, status=0).exclude(parent_id__isnull=True)
            queryset = self.queryset.filter(customer_id=customer_id, status=0, parent_id=None)
            print("queryset=========", queryset)
            for bag in queryset:
                temp_dict = {}
                if bag.parent_id != None:
                    bag = bag.parent_id
                temp_dict['customer_name'] = bag.customer_name
                temp_dict['customer_mobile'] = bag.customer_id
                temp_dict['stored_location_id'] = bag.stored_location_id
                try:
                    bag_info_detail = get_bag_info_by_qrcode(bag.stored_location_id)
                    if bag_info_detail:
                        temp_dict['bag_name'] = bag_info_detail.name
                except Exception as e:
                    print ("get bag info exception", e)
                temp_dict['number_of_bags'] = bag.number_of_bags
                # drop_time = UTC_to_IST_time(bag.drop_time)
                # temp_dict['drop_time'] = bag.drop_time
                temp_dict['drop_time'] = bag.drop_time
                temp_dict['transaction'] = bag.transaction
                temp_dict['shelf'] = bag.shelf
                # temp_dict['location2'] = bag.location2

                try:
                    child_objects = CustomerBag.objects.filter(parent_id=bag.id).order_by('created_on')
                    for child in child_objects:
                        try:
                            # if child.zone:
                            #     profile_obj = ProfileDetails.objects.filter(id=child.location2).first()
                            # else:
                            profile_obj = ProfileDetails.objects.filter(qr_code=child.location2).first()
                            if profile_obj.user_id.first_name:
                                temp_dict['destination'] = 'Collected by ' + str(profile_obj.user_id.first_name)
                            else:
                                temp_dict['destination'] = 'Collected by ' + str(profile_obj.user_id.username)
                        except ProfileDetails.DoesNotExist:
                            print("profile not available for qr code", child.location2)
                            pass

                        if child.shelf:
                            print("Stored at zone", child.shelf)
                            try:
                                shelf_obj = Shelf.objects.get(id=child.shelf)
                                destination_str = 'Stored at ' + str(shelf_obj.zone_id.name)
                                if shelf_obj.zone_id.alias:
                                    destination_str += "(" + shelf_obj.zone_id.alias + ")"

                                temp_dict['destination'] = destination_str
                                temp_dict['shelf'] = child.shelf
                            except shelf_obj.DoesNotExist:
                                print("shelf not available")
                                pass
                        else:
                            pass
                except Exception as e:
                    print("Exception while getting the child info", e)
                    pass
                self.response.append(temp_dict)
            return Response(self.response, status=200)

        elif handler_id and handler_id is not None:
            print("search based on handler============", handler_id)
            print(self.queryset.filter(location2=handler_id, status=0, transaction__in=[0, 2, 6]).query)
            queryset = self.queryset.filter(location2=handler_id, status=0, transaction__in=[0, 2, 6])
            for bag in queryset:
                temp_dict = {}
                if bag.parent_id != None:
                    bag = bag.parent_id
                temp_dict['customer_name'] = bag.customer_name
                temp_dict['customer_mobile'] = bag.customer_id
                temp_dict['stored_location_id'] = bag.stored_location_id
                try:
                    bag_info_detail = get_bag_info_by_qrcode(bag.stored_location_id)
                    if bag_info_detail:
                        temp_dict['bag_name'] = bag_info_detail.name
                except Exception as e:
                    print ("get bag info exception", e)
                temp_dict['number_of_bags'] = bag.number_of_bags
                # drop_time = UTC_to_IST_time(bag.drop_time)
                # temp_dict['drop_time'] = bag.drop_time
                temp_dict['drop_time'] = bag.drop_time
                temp_dict['transaction'] = bag.transaction
                temp_dict['shelf'] = bag.shelf
                temp_dict['status'] = bag.status
                temp_dict['location2'] = bag.location2
                self.response.append(temp_dict)
            return Response(self.response, status=200)


        else:
            self.queryset = []
            return Response(self.response, status=200)
            # return self.queryset

    def post(self, request, *args, **kwargs):
        response = {}
        depos = 0
        deliver = 0
        params = json.loads(request.body.decode('latin1'))
        handler_id = params.get('handler_qr_code', None)
        if handler_id is not None:
            for_deposite = self.queryset.filter(location2=handler_id, status=0).exclude(parent_id=None)

            ######### sakeer code starts ##########

            # for bag in for_deposite:
            #     all_bags = self.queryset.filter(status=0, stored_location_id=bag.stored_location_id,
            #                                     parent_id=bag.parent_id).exclude(id=bag.id)
            #     if all_bags:
            #         for b in all_bags:
            #             if int(b.transaction) == 9:
            #                 deliver += 1
            #             else:
            #                 print("elseeeeee", b.id, b.transaction)
            #
            #     else:
            #         depos += 1
            #
            # response['for_deposite'] = depos
            # # for_delivery = self.queryset.filter(location2=handler_id,transaction__in=[4,5])
            # response['for_delivery'] = deliver
            #
            ############# sakeer's code ends ########

            ############# replace for sakeer's code by kalabha starts ##############

            response['for_deposite'] = for_deposite.exclude(customer_requested=1).count()
            response['deposite'] = BaggageSerializer(for_deposite.exclude(customer_requested=1),
                                                                  many=True).data
            response['delivery'] = BaggageSerializer(for_deposite.filter(customer_requested=1),
                                                                  many=True).data
            response['for_delivery'] = for_deposite.filter(customer_requested=1).count()

            ############# kalabha's code ends ################



        else:
            response['status_code'] = 500
        return Response(response)


class CustomerLocations(ListRetrieveViewSet):
    """
    Description: This class is used to get all the locations
    Author : Sakeer P
    Created At: 30th January 2018

    """
    queryset = Location.objects.filter(status=1)
    serializer_class = LocationSerializer


# class BagTransferSet(CreateViewSet):
#     """
#     This class is used for all the transactions
#     Author : Sakeer p  @ 10-March-2018
#     """
#     queryset = CustomerBag.objects.all()
#     serializer_class = TransferSerializer
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         obj = self.perform_create(serializer)
#         serializer = self.get_serializer(instance=obj)
#         return Response(serializer.data, status=HTTP_201_CREATED)

#     def perform_create(self, serializer):
#         return serializer.create(validated_data=serializer.validated_data)


class CustomerToHanderStoreCreateSet(CreateViewSet):
    """
    Description:  This class is used to create a customer-handler view set
            When customer handover the bag to handler for storing  ( Customer->Handler => Store )
    Author : Sakeer P
    Created At: 24th January 2018

    """
    queryset = CustomerBag.objects.all()
    serializer_class = CustomerHandlerStoreSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_child = self.get_serializer(data=request.data)
        if serializer_child.is_valid(raise_exception=True):
            self.perform_create(serializer, serializer_child)
            response = {}
            response['status'] = 200
            response['message'] = 'Created'
            return Response(response)
            # return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer, serializer_child):
        now = datetime.datetime.now()
        transaction = self.request.data.get('transaction', None)
        handler_id = self.request.data.get('handler_qr_code', None)
        location2 = self.request.data.get('drop_location', None)
        customer_id = self.request.data.get('customer_id', None)
        drop_time = self.request.data.get('drop_time', None)

        parent_obj = serializer.save(location1=handler_id, pick_up_time=now, location2=location2, status=0,
                                     drop_time=drop_time)
        serializer_child.save(location1=customer_id, pick_up_time=now, location2=handler_id, status=0,
                              parent_id=parent_obj, drop_time=drop_time)


class CustomerInitiateDeliveryBagCreateSet(CreateViewSet):
    """
    Description: This class is used to initiate a delivery request by customer
                When Handler initiate a request for customer for handover the bag to Customer for delivery  ( Customer => delivery )
    Author : Sakeer P
    Created At: 31st January 2018

    """
    queryset = CustomerBag.objects.all()
    serializer_class = CustomerInitiateDeliverySerializer

    def create(self, request, *args, **kwargs):
        self.response = {}
        self.response['result'] = []
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            self.response['status'] = 200
            self.response['message'] = 'These bags are initiated for delivery'
            return Response(self.response)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        now = datetime.datetime.now()
        transaction = self.request.data.get('transaction', None)
        location1 = self.request.data.get('handler_qr_code', None)
        location2 = self.request.data.get('location_id', None)
        stored_location_id = self.request.data.get('stored_location_id', None)
        print("storell", stored_location_id)
        print("inputs============handler_qr_code", location1, "transaction=", transaction, "location_id", location2)
        
        sender_list = []
        for store_id in stored_location_id:
            print("store bag id", store_id)
            try:
                parent_obj = CustomerBag.objects.filter(status=0, stored_location_id=store_id, transaction=0,
                                                        parent_id=None).last()

                print("parent-=====", parent_obj)
                try:
                    child_obj = CustomerBag.objects.filter(status=0, stored_location_id=store_id,
                                                           parent_id=parent_obj).last()
                    print("child objj", child_obj)
                    zone = Location.objects.get(id=int(location2))
                    child_obj.customer_requested = 1
                    child_obj.customer_requested_time = now
                    child_obj.customer_requested_place = zone
                    child_obj.save()
                    try:
                        if child_obj.transaction == '11' or child_obj.transaction == 11:
                            receiver = ProfileDetails.objects.filter(qr_code=child_obj.location1).last()
                        else:
                            receiver = ProfileDetails.objects.filter(qr_code=child_obj.location2).last()
                        print("mobile=", receiver.user_id.username, "location1==",parent_obj.customer_name,"location2==",zone.name )
                        
                        if receiver.user_id.username in sender_list:
                            pass
                        else:
                            try:
                                send_message(receiver.user_id.username,parent_obj.customer_name,zone.name,CUSTOMER_REQ)
                                sender_list.append(receiver.user_id.username)
                            except Exception as e:
                                print ("handled excepton", e)
                                pass

                    except Exception as e:
                        raise
                except Exception as e:
                    print(e)
                    pass
                self.response['result'].append(store_id)
            except CustomerBag.DoesNotExist as e:
                print(e)
                return self.response
            except Exception as e:
                print("there is some exception", e)


class HandlerToCustomerDeliveryBagCreateSet(CreateViewSet):
    """
    Description: This class is used to create a Handler-Customer view set
                When Handler handover the bag to Customer for delivery  ( Handler->Customer => delivery )
    Author : Sakeer P
    Created At: 31st January 2018

    """
    queryset = CustomerBag.objects.all()
    serializer_class = HandlerToCustomerDeliverySerializer

    def create(self, request, *args, **kwargs):
        self.response = {}
        self.response['result'] = []
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            self.response['status'] = 200
            self.response['message'] = 'These bags are handovered to customer'
            return Response(self.response)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):

        now = datetime.datetime.now()
        transaction = self.request.data.get('transaction', None)
        location1 = self.request.data.get('handler_qr_code', None)
        location2 = self.request.data.get('customer_id', None)
        stored_location_id = self.request.data.get('stored_location_id', None)
        for store_id in stored_location_id:
            print("store_idstore_id===", store_id)
            try:
                parent_obj = CustomerBag.objects.filter(customer_id=location2, status=0, stored_location_id=store_id,
                                                        transaction=0, parent_id__isnull=True).last()
                cust_obj = []
                print ("get customer childs with status = 1")
                cust_obj = CustomerBag.objects.filter(zone__isnull=False, stored_location_id=store_id, parent_id=parent_obj).last()
                print ("cust obj",cust_obj)
                mobile_numbers = []
                try:
                    # send push notification to zone manager also, so get the mobile number of the zones
                    if cust_obj:
                        print (cust_obj.id)
                        print ("get zone managersss for the zone",cust_obj.zone )
                        zone_managers = get_managers_based_zone_id(cust_obj.zone)
                        print ("zone_managers=======", zone_managers)
                        print ("get mobile number from user ids")
                        mobile_numbers = get_username_from_id_list(zone_managers)
                        print ("mobile numbers are", mobile_numbers)
                        if mobile_numbers:
                            # send push notification to zone managers
                            for mobile in mobile_numbers:
                                print ("send msg for mobile", mobile)
                                send_message(mobile,location1,location2,CUSTOMER_RECEIVE)
                except Exception as e:
                    print ("send push notification to zone manager raised and exception ", e)
                    pass

                child_obj = CustomerBag.objects.filter(status=0, stored_location_id=store_id, parent_id=parent_obj)
                status = 1
                zone = None
                transaction_update_create(parent_obj, child_obj, store_id, transaction, location1, location2, zone,
                                          status)
                self.response['result'].append(store_id)

                


            except Exception as e:
                print(e)
                pass


class HandlerPushNotification(ListRetrieveViewSet):
    queryset = CustomerBag.objects.all()
    serializer_class = BaggageSerializer

    def get_queryset(self):
        self.response = {}
        handler_id = self.request.query_params.get('handler_qr_code', None)
        if handler_id is not None:
            queryset = self.queryset.filter(location2=handler_id, status=0, transaction__in=[1, 5])
            return queryset


class HandlerToHandlerAcceptBagCreateSet(CreateViewSet):
    """
    Description: This class is used to create a Handler-Handler view set
                When Handler handover the bag to another handler for accept  ( Handler->Handler => accept )
    Author : Sakeer P
    Created At: 24th January 2018

    """
    queryset = CustomerBag.objects.all()
    serializer_class = HandlerToHandlerAcceptSerializer

    def create(self, request, *args, **kwargs):
        self.response = {}
        self.response['result'] = []
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            self.response['status'] = 200
            self.response['message'] = 'These bags are accepted by handler'
            return Response(self.response)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        now = datetime.datetime.now()
        transaction = self.request.data.get('transaction', None)
        # ( Handler->Handler => Store )
        location1 = self.request.data.get('handler_qr_code1', None)
        location2 = self.request.data.get('handler_qr_code2', None)
        stored_location_id = self.request.data.get('stored_location_id', None)
        for store_id in stored_location_id:
            try:
                parent_obj = CustomerBag.objects.filter(status=0, stored_location_id=store_id, transaction=0,
                                                        parent_id=None).last()
                child_obj = CustomerBag.objects.filter(status=0, parent_id=parent_obj)
                CustomerObj = CustomerBag.objects.filter(stored_location_id=store_id, parent_id=parent_obj).order_by(
                        'created_on').last()
                if CustomerObj:
                    zone = CustomerObj.zone
                transaction_update_create(parent_obj, child_obj, store_id, transaction, location1, location2, zone)
                self.response['result'].append(store_id)

            except Exception as e:
                print(e)
                pass

        try:
            receiver1 = ProfileDetails.objects.filter(qr_code=location1).last()
            receiver2 = ProfileDetails.objects.filter(qr_code=location2).last()
            mobile = receiver1.user_id.username
            location1 = receiver1.user_id.first_name
            location2 = receiver2.user_id.first_name
            print("mobile=", mobile, "location1==",location1,"location2==",location2 )
            send_message(mobile,location1,location2,HANDLER_TRANSFER)
            print("mobile=", mobile, "location1==",location2,"location2==",location1 )
            mobile = receiver2.user_id.username
            send_message(mobile,location2,location1,HANDLER_RECIEVER)
            

        except Exception as e:
            print ("handled exception", e)
            pass


class HandlerToZoneAcceptCreateSet(CreateViewSet):
    """
    Description: This class is used to create a Handler-Zone view set
                When zoner accept the bag from handler for accept  ( Handler->Zone => Accept )
    Author : Sakeer P
    Created At: 24th January 2018

    """
    queryset = CustomerBag.objects.all()
    serializer_class = HandlerToZoneAcceptSerializer

    def create(self, request, *args, **kwargs):
        self.response = {}
        self.response['result'] = []
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            self.response['status'] = 200
            self.response['message'] = 'These bags are accepted by zoner'
            return Response(self.response)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        print("create HandlerToZoneAcceptCreateSet")
        now = datetime.datetime.now()
        transaction = self.request.data.get('transaction', None)
        location1 = self.request.data.get('handler_qr_code', None)
        location2 = self.request.data.get('zone_manager_qr_code', None)
        stored_location_id = self.request.data.get('stored_location_id', None)
        zone_id = self.request.data.get('zone_id', None)
        try:
            zone = Location.objects.get(id=int(zone_id), category=1)
            for bag_id in stored_location_id:
                try:
                    parent_obj = CustomerBag.objects.filter(status=0, stored_location_id=bag_id, transaction=0,
                                                            parent_id=None).last()
                    child_obj = CustomerBag.objects.filter(status=0, parent_id=parent_obj)
                    

                    # send push notification to old zone manager also if exist,
                    cust_obj = []
                    print ("get customer childs with status = 1")
                    cust_obj = CustomerBag.objects.filter(zone__isnull=False, status=1, stored_location_id=bag_id, parent_id=parent_obj).last()
                    print ("cust obj",cust_obj)
                    mobile_numbers = []
                    try:
                        # send push notification to old zone manager also if exist, so get the mobile number of the zones
                        if cust_obj:
                            print (cust_obj.id)
                            print ("get zone managersss for the zone",cust_obj.zone )
                            zone_managers = get_managers_based_zone_id(cust_obj.zone)
                            print ("zone_managers=======", zone_managers)
                            print ("get mobile number from user ids")
                            mobile_numbers = get_username_from_id_list(zone_managers)
                            print ("mobile numbers are", mobile_numbers)
                            if mobile_numbers:
                                # send push notification to zone managers
                                location1 = receiver1.user_id.first_name
                                location2 = receiver2.user_id.first_name
                                for mobile in mobile_numbers:
                                    print ("send msg for mobile", mobile)
                                    send_message(mobile,location1,location2,HANDLER_TRANSFER)
                    except Exception as e:
                        print ("send push notification to zone manager raised and exception ", e)
                        pass

                    transaction_update_create(parent_obj, child_obj, bag_id, transaction, location1, location2, zone)
                    self.response['result'].append(bag_id)
                except Exception as e:
                    print(e)
                    pass
            try:
                receiver1 = ProfileDetails.objects.filter(qr_code=location1).last()
                receiver2 = ProfileDetails.objects.filter(qr_code=location2).last()
                mobile = receiver1.user_id.username
                location1 = receiver1.user_id.first_name
                location2 = receiver2.user_id.first_name
                print("mobile=", mobile, "location1==",location1,"location2==",location2 )
                send_message(mobile,location1,location2,ZONE_RECIEVER)
                print("mobile=", mobile, "location1==",location2,"location2==",location1 )
                mobile = receiver2.user_id.username
                send_message(mobile,location1,location2,HANDLER_TRANSFER)
            except Exception as e:
                print ("handled exception", e)
                pass
        except Location.DoesNotExist:
            print("location/zone does not exist")
            self.response['result'] = []


class ZoneToHandlerAcceptBagCreateSet(CreateViewSet):
    """
    Description: This class is used to create a Zone-Handler view set
                When handler receives the bag from zoner   ( Zone->Handler => receive )
    Author : Sakeer P
    Created At: 1st February 2018

    """
    queryset = CustomerBag.objects.all()
    serializer_class = ZoneToHandlerAcceptSerializer

    def create(self, request, *args, **kwargs):
        self.response = {}
        self.response['result'] = []
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            self.response['status'] = 200
            self.response['message'] = 'These bags are received from zoner'
            return Response(self.response)
            # return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):

        now = datetime.datetime.now()
        transaction = self.request.data.get('transaction', None)
        location1 = self.request.data.get('zone_manager_qr_code', None)
        location2 = self.request.data.get('handler_qr_code', None)
        stored_location_id = self.request.data.get('stored_location_id', None)
        zone_id = self.request.data.get('zone_id', None)
        try:
            # zone = Location.objects.get(id=int(zone_id), category=1)
            for bag_id in stored_location_id:
                try:
                    parent_obj = CustomerBag.objects.filter(status=0, stored_location_id=bag_id, transaction=0,
                                                            parent_id=None).last()
                    child_obj = CustomerBag.objects.filter(status=0, parent_id=parent_obj)
                    CustomerObj = CustomerBag.objects.filter(stored_location_id=bag_id, parent_id=parent_obj).order_by(
                        'created_on').last()
                    if CustomerObj:
                        zone = CustomerObj.zone
                    transaction_update_create(parent_obj, child_obj, bag_id, transaction, location1, location2, zone)
                    self.response['result'].append(bag_id)
                    send_message(receiver.user_id.username,parent_obj.customer_id,zone.name,CUSTOMER_REQ)
                except Exception as e:
                    print(e)
                    pass

            try:
                receiver1 = ProfileDetails.objects.filter(qr_code=location1).last()
                receiver2 = ProfileDetails.objects.filter(qr_code=location2).last()
                mobile = receiver1.user_id.username
                location1 = receiver1.user_id.first_name
                location2 = receiver2.user_id.first_name
                print("mobile=", mobile, "location1==",location1,"location2==",location2 )
                send_message(mobile,location1,location2,HANDLER_RECIEVER)
                print("mobile=", mobile, "location1==",location2,"location2==",location1 )
                mobile = receiver2.user_id.username
                send_message(mobile,location2,location1,ZONE_TRANSFER)
            except Exception as e:
                print ("handled exception", e)
                pass

        except Location.DoesNotExist:
            self.response['result'] = []


class CustomerToZoneStoreCreateSet(CreateViewSet):
    """
    Description:  This class is used to create a customer-zone view set
            When customer handover the bag to zone for storing  ( Customer->zone => Store )
    Author : Sakeer P
    Created At: 2nd Feb 2018

    """
    queryset = CustomerBag.objects.all()
    serializer_class = CustomerToZoneStoreSerializer

    def create(self, request, *args, **kwargs):
        print("=========================")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        serializer = self.get_serializer(instance=obj)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.create(validated_data=serializer.validated_data)


class ZoneToCustomerDeliveryBagCreateSet(CreateViewSet):
    """
    Description: This class is used to create a Zone-Customer view set
                When Zoner handover the bag to Customer for delivery  ( Zone->Customer => delivery )
    Author : Sakeer P
    Created At: 2nd Feb 2018

    """
    queryset = CustomerBag.objects.all()
    serializer_class = ZoneToCustomerDeliverySerializer

    def create(self, request, *args, **kwargs):
        self.response = {}
        self.response['result'] = []
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            self.response['status'] = 200
            self.response['message'] = 'These bags are handovered to customer'
            return Response(self.response)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):

        now = datetime.datetime.now()
        location1 = self.request.data.get('zone_manager_qr_code', None)
        transaction = self.request.data.get('transaction', None)
        location2 = self.request.data.get('customer_id', None)
        stored_location_id = self.request.data.get('stored_location_id', None)
        zone_id = self.request.data.get('zone_id', None)
        try:
            print("zone ids", zone_id)
            zone = Location.objects.get(id=int(zone_id), category=1)
            for store_id in stored_location_id:
                try:
                    parent_obj = CustomerBag.objects.filter(customer_id=location2, status=0,
                                                            stored_location_id=store_id,
                                                            transaction=0, parent_id=None).last()
                    child_obj = CustomerBag.objects.filter(status=0, stored_location_id=store_id,
                                                           parent_id=parent_obj)
                    status = 1
                    transaction_update_create(parent_obj, child_obj, store_id, transaction, location1, location2, zone,
                                              status)
                    self.response['result'].append(store_id)
                except Exception as e:
                    print(e)
                    pass
        except Location.DoesNotExist:
            self.response['result'] = []


class TamperBagViewSet(ListRetrieveViewSet):
    """
    Description: This class is used to list all the tamper proof bag details or
                    only a specific tamper proof bag details
    Author : Sakeer P
    Created At: 6th Feb 2018

    """
    queryset = Bag.objects.all()
    serializer_class = BagDetailsSerializer

    def list(self, request, *args, **kwargs):
        self.response = []
        self.bag_info = []
        bag_qr_code = self.request.query_params.get('bag_qr_code', None)
        bag_name = self.request.query_params.get('bag_name', None)
        if bag_qr_code is not None or bag_name is not None:
            try:
                bag_obj = Bag.objects.get(qr_code__exact=str(bag_qr_code))
                print("bag_obj====", bag_obj.id)
            except Exception as e:
                try:
                    bag_obj = Bag.objects.get(name__exact=str(bag_name))
                except Exception as e:
                    return Response(self.response, status=200)

            if bag_obj:
                self.bag_dict = {}
                self.bag_dict['stored_location_id'] = bag_obj.qr_code
                self.bag_dict['bag_name'] = bag_obj.name
                self.bag_dict['customer_name'] = ''
                self.bag_dict['customer_mobile'] = ''
                self.bag_dict['number_of_bags'] = ''
                self.bag_dict['drop_time'] = ''
                self.bag_dict['shelf'] = ''
                self.bag_dict['destination_owner_type'] = ''
                self.bag_dict['destination_role_id'] = ''
                self.bag_dict['status'] = 1
                self.get_customer_bag_information()
                self.response.append(self.bag_dict)
        else:
            for bag in self.queryset:
                self.bag_dict = {}
                self.bag_dict['stored_location_id'] = bag.qr_code
                self.get_customer_bag_information()
                self.response.append(self.bag_dict)
        return Response(self.response, status=200)

    def get_customer_bag_information(self):
        try:
            print("Get the information only when bag is not Handover to customer yet")
            customer_bag_binfo = CustomerBag.objects.filter(stored_location_id=self.bag_dict['stored_location_id'],
                                                            parent_id__isnull=True, status=0)
            if customer_bag_binfo:
                print("Bag not yet delivered by customer")
                for customer_info in customer_bag_binfo:
                    self.bag_dict['customer_name'] = customer_info.customer_name
                    self.bag_dict['customer_mobile'] = customer_info.customer_id
                    self.bag_dict['number_of_bags'] = customer_info.number_of_bags
                    self.bag_dict['drop_time'] = customer_info.drop_time
                    # self.bag_dict['drop_time'] = customer_info.created_on
                    # self.bag_dict['transaction'] = customer_info.transaction
                    self.bag_dict['shelf'] = customer_info.shelf
                    self.bag_dict['status'] = 0

                    if customer_info.id:
                        print("customer_info id", customer_info.id)
                        try:
                            child_objects = CustomerBag.objects.filter(parent_id=customer_info.id, status=0)
                            for child in child_objects:
                                if child.status == 0 and child.location2 != '':
                                    print(
                                        "It is with hander/zone manager so get the user_id from profile table using the qr of location2 and find the username")
                                    print("child status==", child.status, "child location2 id==", child.location2)
                                    try:
                                        profile_obj = ProfileDetails.objects.filter(qr_code=child.location2).first()
                                        print("profile obbjj==", profile_obj)
                                        if profile_obj.user_id.first_name:
                                            self.bag_dict['destination'] = 'Collected by ' + str(
                                                profile_obj.user_id.first_name)
                                            self.bag_dict['destination_owner_type'] = profile_obj.role.name
                                            self.bag_dict['destination_role_id'] = profile_obj.role.id
                                        else:
                                            self.bag_dict['destination'] = 'Collected by ' + str(
                                                profile_obj.user_id.username)
                                            self.bag_dict['destination_owner_type'] = profile_obj.role.name
                                            self.bag_dict['destination_role_id'] = profile_obj.role.id
                                    except Exception as e:
                                        print("Exception while getting the profile info", child.location2, e)

                                    if child.shelf and child.shelf != '':
                                        print("Stored at zone", child.shelf)
                                        try:
                                            shelf_obj = Shelf.objects.get(id=child.shelf)
                                            self.bag_dict['shelf'] = shelf_obj.id
                                            destination_str = 'Stored at ' + str(shelf_obj.zone_id.name)
                                            if shelf_obj.zone_id.alias:
                                                destination_str += "(" + shelf_obj.zone_id.alias + ")"

                                            self.bag_dict['destination'] = destination_str

                                            self.bag_dict['destination_owner_type'] = 'Zone Manager'
                                        except shelf_obj.DoesNotExist:
                                            print("shelf not available")
                                            pass
                                    else:
                                        pass



                                else:
                                    print("else === child status==", child.status, "child location2 id==",
                                          child.location2)
                        except Exception as e:
                            print("Exception while getting the child dinfo", e)

                            pass



            else:
                print("Bag delivered to customer")
                # customer_bag_binfo = CustomerBag.objects.filter(stored_location_id=self.bag_dict['stored_location_id'],
                #                                                 parent_id=None, status=1)
                # if customer_bag_binfo:
                #     print("Bag delivered information of customer")
                #     for customer_info in customer_bag_binfo:
                #         self.bag_dict['customer_name'] = customer_info.customer_name
                #         self.bag_dict['customer_mobile'] = customer_info.customer_id
                #         self.bag_dict['number_of_bags'] = customer_info.number_of_bags
                #         self.bag_dict['shelf'] = customer_info.shelf
                #         self.bag_dict['destination'] = customer_info.customer_name
                #         self.bag_dict['destination_owner_type'] = 'Customer'
                #         self.bag_dict['drop_time'] = customer_info.drop_time
                #         self.bag_dict['drop_time'] = UTC_to_IST_time(customer_info.created_on)
                #         # self.bag_dict['transaction'] = customer_info.transaction
                #         self.bag_dict['destination_role_id'] = 4

                # else:
                #     print("No customer info available")
                    # self.bag_dict = {}

            # try:
            #     if self.bag_dict['destination_role_id'] == 4 or self.bag_dict['destination_role_id'] == '':
            #         self.bag_dict['status'] = 1
            #     else:
            #         self.bag_dict['status'] = 0
            # except Exception as e:
            #     self.bag_dict['status'] = 0
            #     print("Exception while checking bag is in use or not", e)

        except Exception as e:
            print("Exception in bag info", e)


def utc_to_local(date_input):
    """date_input is a datetime object containing a tzinfo

    Returns a datetime object at Manila time.
    """

    manila = Manila()
    tzoffset = manila.utcoffset()
    date = (date_input + tzoffset).replace(tzinfo=manila)
    return date


class GetTamperBaHistoryViewSet(ListRetrieveViewSet):
    """
    Description: This class is used to get the history of a bag using qrcode
                    only a specific tamper proof bag history
    Author : Sakeer P
    Created At: 7th Feb 2018

    """
    queryset = Bag.objects.all()
    serializer_class = BagDetailsSerializer

    def list(self, request, *args, **kwargs):
        print("list")
        # self.response = {}
        self.response = []
        self.bag_dict = []

        self.bag_qr_code = self.request.query_params.get('bag_qr_code', None)
        print("self.bag_qr_code===", self.bag_qr_code)
        if self.bag_qr_code is not None:
            try:
                # bag_obj = Bag.objects.filter(qr_code=self.bag_qr_code)
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM api_baggage_bag WHERE qr_code like binary %s", [self.bag_qr_code])
                bag_obj = cursor.fetchone()
                print("bag obj", bag_obj)
            except Exception as e:
                print("exception==", e)
                return Response(self.response, status=200)
            if bag_obj:
                self.get_customer_bag_information()
                # self.response.append(self.response)
        else:
            pass
        return Response(self.response, status=200)

    def get_customer_bag_information(self):
        try:
            print("Get the information only when bag is not Handover to customer yet")
            customer_info = CustomerBag.objects.filter(stored_location_id=self.bag_qr_code, parent_id__isnull=True,
                                                           status=0).last()
            print("customer_bag_info==", customer_info)
            index = 0
            if customer_info:
                print("Bag not yet delivered by customer")
                try:
                    child_objects = CustomerBag.objects.filter(parent_id=customer_info.id).order_by('created_on')
                    print("child_objects==", child_objects)
                    for child in child_objects:
                        history = {}
                        origin_user_name = ''
                        dest_user_name = ''
                        origin_user_name = get_profile_first_name_frm_qr_code(child.location1)
                        dest_user_name = get_profile_first_name_frm_qr_code(child.location2)
                        history['time'] = get_action_time(child)
                        history['message'] = get_action_message(origin_user_name,dest_user_name,child)

                        if child.shelf and child.shelf != '':
                            print("Stored at shelf", child.shelf)
                            history['message'] = get_shelf_action_message(child)
                        else:
                            pass
                        index += 1
                        history['id'] = index
                        self.response.append(history)
                except Exception as e:
                    print("Exception while getting the child info", e)
                    pass
            else:
                print("Bag delivered to customer")
        except Exception as e:
            print("Exception in bag info", e)


class PhysicalLocationList(generics.ListAPIView):
    serializer_class = PhysicalLocationSerializer
    queryset = PhysicalLocation.objects.all()


class GetTamperBagHistoryViewSet(generics.ListAPIView):
    def get_queryset(self):
        try:
            bag = Bag.objects.get(qr_code=self.request.query_params.get('bag_qr_code', False))
            return CustomerBag.objects.filter(stored_location_id=bag.qr_code,
                                              status=0)
        except Bag.DoesNotExist:
            return 0

    serializer_class = BagHistorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset == 0:
            return Response({'message': 'No tamper bag'})
        elif queryset:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({'message': 'Bag is not in use'})
