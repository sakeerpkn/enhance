from django.core.exceptions import FieldError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view

from .models import UserOTP, ProfileDetails
from api.api_zone.models import ZoneToZoneManagerMapping
from django.contrib.auth.models import User, Group
from .serializers import UserSerializer, UserUpdateSerializer, ProfileSerializer, \
    UserLoginSerializer, UserCreateSerializer
from customer.serializers import CustomCustomerSerializer
from rest_framework import mixins, generics, viewsets
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.db import connection
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
import json
import random
import string
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt


class ListRetrieveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class CreateViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class UpdateViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


# class CreateUserOtpSet(CreateViewSet):
#     queryset = UserOTP.objects.all()
#     serializer_class = UserOTPSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             otp = randint(1000, 9999)
#             serializer.save(otp=otp)
#             response = {}
#             response['status'] = 200
#             response['result'] = otp
#             return Response(response)
#         return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


# class VerifyUserOtpSet(UpdateViewSet):
#     queryset = UserOTP.objects.all()
#     serializer_class = UserOTPSerializer

#     def put(self, request, *args, **kwargs):
#         response = {}
#         try:
#             response['status'] = 500
#             query_params = json.loads(request.body.decode('latin1'))
#             mobile_number = query_params.get('mobile_number', None)
#             otp = query_params.get('otp', None)
#             if mobile_number is not None and otp is not None:
#                 self.queryset = UserOTP.objects.get(mobile_number=mobile_number, otp=otp, status=0)
#                 self.queryset.status = 1
#                 self.queryset.save()
#                 response['status'] = 200
#         except Exception as e:
#             print("Exception", e)
#             response['status'] = 500
#         return Response(response)


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


class ListZonersHandlersView(ListRetrieveViewSet):
    """
    Description: This class is used to list handlers and zone managers details

    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        user_info_list = []
        user_id = self.request.data.get('user_id', None)
        cursor = connection.cursor()
        cursor.execute(
            "select auth_user.id,auth_user.username,auth_user.first_name,auth_user_groups.group_id from auth_user left join auth_user_groups on auth_user.id = auth_user_groups.user_id where is_staff = 1 and is_active = 1 and is_superuser = 0")
        userset = dictfetchall(cursor)
        user_mobile = self.request.query_params.get('user_mobile', None)
        user_name = self.request.query_params.get('user_name', None)
        if user_mobile is not None:
            # userset = filter(lambda x: x['username'] in user_mobile, userset)
            userset = filter(lambda x: x['username'].startswith(user_mobile), userset)
        if user_name is not None:
            userset = filter(lambda x: user_name.lower() in x['first_name'].lower(), userset)
        for user in userset:

            if user['group_id'] == 2:

                user_info = {}
                user_info['id'] = user['id']
                user_info['user_name'] = user['first_name']
                user_info['user_mobile'] = user['username']
                user_info['user_type'] = user['group_id']
                user_info['zones'] = []
                user_info['zones_alias'] = []
                user_info['zones_id'] = []
                user_info['zones_list'] = []
                zone_mapping_obj = ZoneToZoneManagerMapping.objects.filter(manager_id=user['id'])
                if zone_mapping_obj:
                    zone_list = []
                    for single in zone_mapping_obj:
                        zone_id = single.zone_id.id
                        zone_name = single.zone_id.name
                        alias = single.zone_id.alias

                        zone_dict = {'id': zone_id, 'name': zone_name, 'alias': alias}
                        zone_list.append(zone_dict)

                        user_info['zones'].append(zone_name)
                        user_info['zones_alias'].append(alias)
                        user_info['zones_id'].append(zone_id)
                    user_info['zones_list'] = zone_list
                else:
                    user_info['zones'] = []
                    user_info['zones_alias'] = []
                    user_info['zones_id'] = []
                user_info_list.append(user_info)
            elif user['group_id'] == 3:

                user_info = {}
                user_info['id'] = user['id']
                user_info['user_name'] = user['first_name']
                user_info['user_mobile'] = user['username']
                user_info['user_type'] = user['group_id']
                user_info_list.append(user_info)
            else:

                pass

        return Response(user_info_list)
    # return user_info_list


class UpdateZonersHandlersData(UpdateViewSet):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

    def put(self, request, *args, **kwargs):
        response = {}
        try:
            response['status'] = 500
            query_params = json.loads(request.body.decode('latin1'))
            user_id = query_params.get('user_id', None)
            user_name = query_params.get('user_name', None)
            user_mobile = query_params.get('user_mobile', None)
            if user_id:
                try:
                    user_obj = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    response['status'] = 500
                if user_obj:
                    user_obj.username = user_mobile
                    user_obj.first_name = user_name
                    user_obj.save()
                    response['status'] = 200
        except Exception as e:
            print("Exception", e)
            response['status'] = 500
        return Response(response)


class UserLogin(ListRetrieveViewSet):
    """
    Description: This class is used to login handler and zone managers

    """
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):

        self.response = []
        temp_dict = {}
        try:
            user_name = self.request.data.get('user_name', None)
            user_password = self.request.data.get('user_password', None)

            if user_name and user_password:
                try:
                    user_obj = authenticate(username=user_name, password=user_password)
                    if user_obj:
                        temp_dict['status'] = 200
                        temp_dict['user_id'] = user_obj.id
                        temp_dict['user_mobile'] = user_obj.username
                        temp_dict['user_name'] = user_obj.first_name

                        try:
                            profile_objects = ProfileDetails.objects.filter(user_id=user_obj.id)
                        except ProfileDetails.DoesNotExist:
                            print("does not exist")

                        temp_dict['role_id'] = []
                        temp_dict['role_type'] = []
                        for profile_obj in profile_objects:
                            temp_dict['user_code'] = profile_obj.qr_code
                            if profile_obj.role:
                                temp_dict['role_id'].append(profile_obj.role.id)
                                temp_dict['role_type'].append(profile_obj.role.name)

                                if profile_obj.role.id == 2:
                                    temp_dict['zone_list'] = {}
                                    temp_dict['zones_id'] = []
                                    temp_dict['zones'] = []
                                    zone_list = []
                                    zone_mapping_obj = ZoneToZoneManagerMapping.objects.filter(manager_id=user_obj.id)
                                    if zone_mapping_obj:
                                        for zone_map in zone_mapping_obj:
                                            print("zone_map============", zone_map.zone_id)
                                            temp_dict['zones'].append(zone_map.zone_id.name)
                                            temp_dict['zones_id'].append(zone_map.zone_id.id)

                                            zone_dict = {}
                                            zone_dict['zone_name'] = zone_map.zone_id.name
                                            zone_dict['zone_alias_name'] = zone_map.zone_id.alias
                                            zone_dict['zone_id'] = zone_map.zone_id.id
                                            zone_list.append(zone_dict)
                                        temp_dict['zone_list'] = zone_list

                                    else:
                                        temp_dict['zones'] = []
                                        temp_dict['zones_id'] = []
                                        temp_dict['zone_list'] = {}
                            else:
                                temp_dict['role_id'] = ''
                                temp_dict['role_type'] = ''

                    else:
                        try:
                            user_obj_child = User.objects.get(username=user_name)
                            if user_obj_child:
                                temp_dict['status_message'] = "Invalid Password"
                                temp_dict['status'] = 500
                        except User.DoesNotExist:
                            temp_dict['status_message'] = "Invalid Username"
                            temp_dict['status'] = 500
                        print(temp_dict)
                # self.response.append(temp_dict)

                except Exception as e:
                    print(e)
            else:
                temp_dict['status'] = 500
        except Exception as e:
            print("Exception", e)
            temp_dict['status'] = 500
        self.response.append(temp_dict)
        return Response(self.response)


class HandlerDataViewSet(ListRetrieveViewSet):
    """
    Description: This class is used to list all the handler details
    """
    queryset = ProfileDetails.objects.all()
    serializer_class = ProfileSerializer

    def list(self, request, *args, **kwargs):
        self.response = []
        handler_code = self.request.query_params.get('qr_code', None)
        temp_dict = {}
        temp_dict['role_id'] = []
        temp_dict['role_type'] = []
        temp_dict['zones'] = []
        temp_dict['zones_alias'] = []
        temp_dict['zones_id'] = []
        temp_dict['zone_list'] = {}
        if handler_code:
            profile_objects = ProfileDetails.objects.filter(qr_code=handler_code)
            if profile_objects:
                for profile_obj in profile_objects:
                    temp_dict['user_id'] = profile_obj.user_id.id
                    temp_dict['user_name'] = profile_obj.user_id.first_name
                    temp_dict['user_mobile'] = profile_obj.user_id.username

                    temp_dict['user_code'] = profile_obj.qr_code
                    if profile_obj.role:
                        temp_dict['role_id'].append(profile_obj.role.id)
                        temp_dict['role_type'].append(profile_obj.role.name)
                        if profile_obj.role.id == 2 or profile_obj.role.id == 3:
                            # temp_dict['zones'] = []
                            # temp_dict['zones_id'] = []
                            zone_mapping_obj = ZoneToZoneManagerMapping.objects.filter(manager_id=profile_obj.user_id)
                            if zone_mapping_obj:
                                zone_list = []
                                for single in zone_mapping_obj:
                                    zone_dict = {}
                                    zone_dict['zone_name'] = single.zone_id.name
                                    zone_dict['zone_alias_name'] = single.zone_id.alias
                                    zone_dict['zone_id'] = single.zone_id.id
                                    
                                    zone_id = single.zone_id.id
                                    zone_name = single.zone_id.name
                                    alias = single.zone_id.alias
                                    # zone_dict = {'id': zone_id, 'name': zone_name, 'alias': alias}
                                    zone_list.append(zone_dict)


                                    temp_dict['zones'].append(zone_name)
                                    temp_dict['zones_alias'].append(alias)
                                    temp_dict['zones_id'].append(zone_id)

                                temp_dict['zones_id'] = list(set(temp_dict['zones_id']))
                                temp_dict['zones'] = list(set(temp_dict['zones']))
                                temp_dict['zones_alias'] = list(set(temp_dict['zones_alias']))
                                # temp_dict['zone_list'] = zone_list
                                temp_dict['zone_list'] = zone_list
                            else:
                                temp_dict['zone_list'] = []
                                temp_dict['zones_id'] = []
                    else:
                        temp_dict['role_id'] = []
                        temp_dict['role_type'] = []
                        temp_dict['zones'] = []
                        temp_dict['zones_id'] = []
            self.response.append(temp_dict)
        else:
            temp_dict['status'] = 500
            self.response.append(temp_dict)
        return Response(self.response)


class CreateZonerHandlerSet(CreateViewSet):
    """
    user creation
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            username = self.request.data.get('username', None)
            password = self.request.data.get('password', None)
            first_name = self.request.data.get('first_name', None)
            user_role = self.request.data.get('user_role', None)

            user = User.objects.create_user(username=username, first_name=first_name, password=password, is_staff=1)
            user_qrcode = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            if user.id:
                try:
                    for role in user_role:
                        group_obj = Group.objects.get(id=role)
                        # user_profile_obj = ProfileDetails(qr_code=user_qrcode, user_id=user, role=group_obj)
                        user_profile_obj, created = ProfileDetails.objects.get_or_create(user_id=user, role=group_obj,
                                                                                         defaults={
                                                                                             'qr_code': user_qrcode,
                                                                                             'user_id': user,
                                                                                             'role': group_obj})
                        # user_profile_obj.save()
                        group_obj.user_set.add(user)
                except Exception as e:
                    print(e)
                    pass

            response = {}
            response['status'] = 200
            response['result'] = user.id
            return Response(response)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ZoneManagerList(generics.ListAPIView):
    serializer_class = UserLoginSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        zone_id = self.request.query_params.get('zone_id', None)
        if zone_id:
            user_ids = ZoneToZoneManagerMapping.objects.filter(zone_id=zone_id).values_list('manager_id',flat=True)
            user_ids = ProfileDetails.objects.filter(user_id__in=user_ids,role__id=2).values_list('user_id', flat=True)
        else:
            user_ids = ProfileDetails.objects.filter(role__id=2).values('user_id__id')

        queryset= User.objects.filter(id__in=user_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# class CustomerRetrieve(APIView):
#
#     def get(self, request, pk, format=None):
#         user = get_object_or_404(User, pk=pk)
#         try:
#             address = AddressForUser.objects.get(user=user)
#         except AddressForUser.DoesNotExist:
#             pass
#         try:
#             profile = ProfileDetails.objects.get(user_id=user)
#             try:
#                 customer = CustomerDetail.objects.get(user=profile)
#
#             except CustomerDetail.DoesNotExist:
#                 pass
#
#         except ProfileDetails.DoesNotExist:
#             pass
#         customer_detail = {}
#         user_serializer = CustomerUserSerializer(user)
#         customer_serializer = CustomerDetailSerializer(customer)
#         address_serializer = CustomerAddressSerializer(address)
#         customer_detail['user'] = user_serializer.data
#         customer_detail['customer'] = customer_serializer.data
#         customer_detail['address'] = address_serializer.data
#         return Response(customer_detail)


class CustomerCreate(generics.CreateAPIView):
    serializer_class = CustomCustomerSerializer


def get_otp(code, mobile_number):
    try:
        otp = UserOTP.objects.get(mobile_number=mobile_number, otp=code)
        print ('ddd')
        return otp

    except (TypeError, UserOTP.DoesNotExist, FieldError):
        return None


@api_view(['POST', ])
@csrf_exempt
def request_for_otp(request):
    otp_fun_lst = ['handover', 'accept']
    otp_fun = request.data.get('status', None)

    otp = UserOTP.objects.create(mobile_number=request.data['mobile_number'])
    if otp_fun not in otp_fun_lst: otp_fun = None
    otp.send_otp_as_sms(otp_fun=otp_fun)
    return Response(status=HTTP_200_OK)


@api_view(['POST', ])
def otp_verification(request):
    message = None
    if request.data['mobile_number'] and request.data['code']:
        otp = get_otp(code=request.data['code'], mobile_number=request.data['mobile_number'])

        if otp:
            if otp.is_active():
                key = None
                try:
                    user = User.objects.get(username=request.data['mobile_number'])
                    if not user.is_active:
                        user.make_user_active()
                    auth_login(request, user)
                    token = Token.objects.create(user=user)
                    message = 'Login Success'
                    key = token.key
                except User.DoesNotExist:
                    message = 'Verified'
                otp.delete()
                return Response({'message': message, 'token': key}, status=HTTP_200_OK)

            else:
                message = 'OTP Expired. Try to login again!!'
        else:
            message = 'Invalid OTP. Try again'

    else:
        message = 'Inputs are missing'
    return Response({'message': message}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
def customer_logout(request):
    try:
        token = Token.objects.get(key=request.data['token'], user__id=request.data['user_id'])
        token.delete()
    except Token.DoesNotExist:
        pass
    auth_logout(request)
    return Response({'message': "Logout Success"}, status=HTTP_200_OK)
