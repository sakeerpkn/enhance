from datetime import datetime

from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, \
    authentication_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from api.api_user.serializers import CustomerProfileUserSerializer, UserEditSerializer
from api.api_user.views import get_otp
from base_app.filters import ShopFilter
from base_app.models import BaseShopCategory, Shop, Profession, NhanceDocuments
from base_app.serializers import BaseShopCategorySerializer
from customer.filter import NewsFeedFilter, EarnActionFilter, BurnActionFilter
from customer.pagination import StandardResultsSetPagination

from newsfeed.models import NewsFeed, NewsFeedUserLike

from customer.models import ImageGallery, CustomerQueryType, CustomerQuery, \
    CustomerSocialMediaConnection, CustomerInvite
from customer.serializers import ImageGalleryShortSerializer, ShopSerializer, EarnActionDetailSerializer, \
    BurnActionDetailSerializer, NewsFeedSerializer, EarnTransactionSerializer, BurnTransactionSerializer, \
    SummarySerializer, CustomerQueryTypeShortSerializer, CustomerProfileSerializer, \
    CustomerDetailSerializer, CustomerInviteShortSerializer, BurnTransactionDetailSerializer, \
    NhanceDocumentsSerializer
from api.api_ern_burn.models import EarnTransaction, BurnTransaction, \
    Summary
from customer.utils import earned_points_greater_burned_points, earn_points, user_qrcode, \
    membership_completion_percentage, profile_completion_percentage, check_bag_transaction_active, \
    generate_customer_referral_code, earn_referral_points, check_coupon_expired

from api.api_ern_burn.models import BurnActionDetail, EarnActionDetail
from api.api_user.models import CustomerDetail, AddressForUser, ProfileDetails
from django.contrib.auth import login as auth_login


class ShopCategoryList(generics.ListAPIView):
    serializer_class = BaseShopCategorySerializer
    queryset = BaseShopCategory.objects.filter(status=1).order_by('name')
    pagination_class = StandardResultsSetPagination


class ShopList(generics.ListAPIView):
    serializer_class = ShopSerializer
    queryset = Shop.objects.filter(status=1).order_by('name')
    filter_backends = (DjangoFilterBackend,)
    filter_class = ShopFilter
    pagination_class = StandardResultsSetPagination


class HomeList(APIView):
    '''
        Sending the details for customer app - home page
    '''

    def get(self, request):
        response_dict = {}
        img_list = ImageGallery.objects.filter(image_type=1, is_active=True)[:4]
        newsfeed_list = NewsFeed.objects.filter(status=True).order_by('-id')[:8]

        burnaction_list = BurnActionDetail.objects.filter(status=True, validity_date__gte=timezone.now()).order_by(
            '-action_id')[:2]
        earnaction_list = EarnActionDetail.objects.filter(status=True, validity_date__gte=timezone.now()).order_by(
            '-action_id')[:2]

        response_dict['banner_images'] = ImageGalleryShortSerializer(img_list, many=True).data
        response_dict['newsfeeds'] = NewsFeedSerializer(newsfeed_list, many=True).data
        response_dict['burn_actions'] = BurnActionDetailSerializer(burnaction_list, many=True).data
        response_dict['earn_actions'] = EarnActionDetailSerializer(earnaction_list, many=True).data

        return Response(response_dict)


class ShopRetrieve(generics.RetrieveAPIView):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()


class CouponRetrieve(generics.RetrieveAPIView):
    serializer_class = EarnActionDetailSerializer
    queryset = EarnActionDetail.objects.all()


class NewsFeedList(generics.ListAPIView):
    serializer_class = NewsFeedSerializer
    queryset = NewsFeed.objects.filter(status=1).order_by('-id')
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = NewsFeedFilter


class NewsFeedBannerList(generics.ListAPIView):
    serializer_class = ImageGalleryShortSerializer
    queryset = ImageGallery.objects.filter(is_active=1, image_type=3)


@api_view(['POST'])
def user_activity_for_news(request):
    if request.user.is_authenticated():
        attend = None
        like = None
        if 'attend' in request.data:
            attend = request.data['attend']
        if 'like' in request.data:
            like = request.data['like']
        if attend is not None or like is not None:
            try:
                news = NewsFeed.objects.get(id=request.data['news'])
            except NewsFeed.DoesNotExist:
                return Response({'message': "NewsFeed doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

            try:
                nf = NewsFeedUserLike.objects.get(user=request.user, news_feed=news)
                if like is not None:
                    old_status = nf.status
                    nf.status = like

                    if old_status == 0 and nf.status == 1:
                        news.number_of_likes = news.number_of_likes + 1
                    elif (old_status == 1 and nf.status == 0) and (not news.number_of_likes == 0):
                        news.number_of_likes = news.number_of_likes - 1

                if attend is not None:
                    old_attend = nf.attending
                    nf.attending = attend

                    if (old_attend == 0 or old_attend == None) and nf.attending == 1:
                        news.number_of_attending = news.number_of_attending + 1
                        news.save()
                    elif (old_attend == 1 and nf.attending == 0) and (not news.number_of_attending == 0):
                        news.number_of_attending = news.number_of_attending - 1
                        news.save()

                nf.save()

                news.save()

            except NewsFeedUserLike.DoesNotExist:
                user_activity = NewsFeedUserLike.objects.create(user=request.user, status=like, news_feed=news,
                                                                attending=attend)
                if user_activity.status == 1:
                    news.number_of_likes = news.number_of_likes + 1

                if user_activity.attending == 1:
                    news.number_of_attending = news.number_of_attending + 1

                news.save()
        return Response({'like': like, 'attend': attend})
    return Response({'message': 'Login Required'}, status=status.HTTP_403_FORBIDDEN)


class EarnActionDetailList(generics.ListAPIView):
    serializer_class = EarnActionDetailSerializer
    pagination_class = (StandardResultsSetPagination)
    filter_backends = (DjangoFilterBackend,)
    filter_class = EarnActionFilter

    def get_queryset(self):
        return EarnActionDetail.objects.filter(status=1, validity_date__gte=timezone.now())


class BurnActionDetailList(generics.ListAPIView):
    serializer_class = BurnActionDetailSerializer
    pagination_class = (StandardResultsSetPagination)
    filter_backends = (DjangoFilterBackend,)
    filter_class = BurnActionFilter

    def get_queryset(self):
        return BurnActionDetail.objects.filter(status=1, validity_date__gte=timezone.now())


class EarnTransactionViewSet(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    serializer_class = EarnTransactionSerializer

    def get_queryset(self):
        earn_transaction = EarnTransaction.objects.filter(user=self.request.user, status=1).order_by('-id')
        earn_transaction.update(is_viewed=True)
        return earn_transaction

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        earned_action = request.data.get('erned_action')
        try:
            earned_action = EarnActionDetail.objects.get(action_id=earned_action)
        except:
            return Response({'message': 'Invalid Earned Action', 'status': 0}, status=status.HTTP_400_BAD_REQUEST)
        try:
            EarnTransaction.objects.get(erned_action=earned_action, user=request.user)
            return Response({'message': 'You have already earned this', 'status': 0},
                            status=status.HTTP_400_BAD_REQUEST)

        except:
            pass
        instance = self.perform_create(serializer, user=request.user, earned_action=earned_action)
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer, user=None, earned_action=None):
        return serializer.create(validated_data=serializer.validated_data, user=user, earned_action=earned_action)


class BurnTransactionViewSet(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        return BurnTransaction.objects.filter(user=self.request.user, status=1, purchased=1).order_by('-id')

    serializer_class = BurnTransactionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        burned_action = request.data.get('burned_action')
        try:
            burned_action = BurnActionDetail.objects.get(action_id=burned_action)
        except Exception as e:
            return Response({'message': 'Invalid Burned Action', 'status': 0}, status=status.HTTP_400_BAD_REQUEST)

        if earned_points_greater_burned_points(burned_points=request.data['burned_points'], user=request.user):
            serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer, user=request.user, burned_action=burned_action)
            serializer = self.get_serializer(instance=instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'message': 'Earn more points to burn', 'status': 0}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer, user=None, burned_action=None):
        return serializer.create(validated_data=serializer.validated_data, user=user, burned_action=burned_action)


class ProfileSummary(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = Summary.objects.get(user=request.user)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except:
            return {'status': 0, 'message': "No summary Available"}

    serializer_class = SummarySerializer


class CustomerQueryView(APIView):
    '''
        get: Return the list of all the available query types
        post: Add customer query
    '''

    def get(self, request):

        response_dict = {}
        query_type_lst = CustomerQueryType.objects.filter(is_active=True).order_by('-title')
        response_dict['query_types'] = CustomerQueryTypeShortSerializer(query_type_lst, many=True).data
        return Response(response_dict)

    def post(self, request):

        cust_id = request.data.get('customer_id')
        query = request.data.get('query', '')
        query_type = request.data.get('query_type', '')

        try:
            cust_detail_obj = CustomerDetail.objects.get(user__qr_code=cust_id)
        except:
            return Response({'status': 0, 'message': 'Invalid customer id.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            query_type_obj = CustomerQueryType.objects.get(id=query_type, is_active=True)
        except:
            return Response({'status': 0, 'message': 'Invalid Query type.'}, status=status.HTTP_404_NOT_FOUND)
        if not query.strip():
            return Response({'status': 0, 'message': 'Query field is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        CustomerQuery.objects.create(
            customer=cust_detail_obj,
            query=query,
            query_type=query_type_obj
        )
        return Response({'status': 1, 'message': 'Query added successfully.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def check_for_recent_coupons(request):
    if request.user.is_authenticated():
        if EarnTransaction.objects.filter(is_viewed=False):
            return Response({'recent_coupons': True}, status=status.HTTP_200_OK)
        return Response({'recent_coupons': False}, status=status.HTTP_200_OK)
    return Response({'message': "Login Required"}, status=status.HTTP_403_FORBIDDEN)


class CustomerRetrieve(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, **kwargs):
        user = get_object_or_404(ProfileDetails, user_id=request.user)
        user_serializer = UserEditSerializer(request.user)
        customer = get_object_or_404(CustomerDetail, user=user)
        customer_serializer = CustomerDetailSerializer(customer)
        completed = False
        try:
            EarnTransaction.objects.get(user=request.user, erned_action__name='Complete Profile')
            completed = True
        except ObjectDoesNotExist:
            pass
        membership_completion = membership_completion_percentage(request.user)
        profile_completion = profile_completion_percentage(request.user, customer)

        return Response({'user': user_serializer.data, 'profile': customer_serializer.data, 'Completed': completed,
                         'membership_completion': membership_completion, 'profile_completion': profile_completion})

    def update(self, request, customer_id, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = CustomerDetail.objects.get(user__qr_code=customer_id)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        username = request.data['user']['username']
        dob = request.data['profile']['date_of_birth']
        dob_obj = None
        if dob:
            try:
                dob_obj = datetime.strptime(dob, '%Y-%m-%d')
            except Exception as e:
                print(e)
                return Response({'status': 0, "message": "Invalid date of birth."})

        if username != request.user.username:
            if check_bag_transaction_active(request.user):
                return Response({'message': "Please complete your current bag transaction"},
                                status=status.HTTP_403_FORBIDDEN)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer, user=request.user, instance=instance, username=username, dob_obj=dob_obj)
        return Response({'message': "Profile Updated", "status": 1}, status=status.HTTP_200_OK)

    def perform_update(self, serializer, user, instance, username, dob_obj):
        point = 0
        with transaction.atomic():
            user.username = username

            if serializer.validated_data['user']['first_name']:
                user.first_name = serializer.validated_data['user']['first_name']
                point = point + 1
            if serializer.validated_data['user']['email']:
                user.email = serializer.validated_data['user']['email']
                point = point + 1
            user.save()
            if serializer.validated_data['profile']['profession']:
                try:
                    profession = Profession.objects.get(name=serializer.validated_data['profile']['profession'])
                    instance.profession = profession
                    point = point + 1
                except ObjectDoesNotExist:
                    pass
            if serializer.validated_data['profile']['favourite_shop']:
                try:
                    shop = Shop.objects.get(name=serializer.validated_data['profile']['favourite_shop'])
                    instance.favourite_shop = shop
                    point = point + 1
                except ObjectDoesNotExist:
                    pass
            if serializer.validated_data['profile']['address']:
                instance.address = serializer.validated_data['profile']['address']
                point = point + 1
            if dob_obj and instance.date_of_birth is None:
                earn_points(user=user, action='Add DOB and Earn')
                update_dob(self.request)
                instance.date_of_birth = dob_obj
            if point == 5:
                earn_points(user=user, action='Complete Profile')
            instance.save()

    queryset = CustomerDetail.objects.all()
    serializer_class = CustomerProfileSerializer


@csrf_exempt
@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def update_dob(request):
    try:
        customer = CustomerDetail.objects.get(user__user_id=request.user)
        old_dob = customer.date_of_birth
        customer.date_of_birth = request.data['dob']
        customer.save()
        if not old_dob:
            earn_points(user=request.user, action='Add DOB and Earn')
        message = "D.O.B updated"
        code = status.HTTP_200_OK
    except CustomerDetail.DoesNotExist:
        message = "Customer does not exist"
        code = status.HTTP_404_NOT_FOUND
    return Response({'message': message}, status=code)


@method_decorator(csrf_exempt, name='dispatch')
class AddProfile(generics.CreateAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            customer = CustomerDetail.objects.get(user__user_id=request.user)
        except:
            return Response({'status': '0', 'message': 'User Not found'},
                            status=status.HTTP_400_BAD_REQUEST)

        register_using = request.data.get('register_using', '')
        if register_using and register_using not in ['google', 'facebook']:
            return Response({'status': '0', 'message': 'Invalid data given.'}, status=status.HTTP_400_BAD_REQUEST)
        dob = request.data['profile']['date_of_birth']
        dob_obj = None
        if dob:
            try:
                dob_obj = datetime.strptime(dob, '%Y-%m-%d').date()
            except Exception as e:
                return Response({'status': 0, "message": "Invalid date of birth."})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.first_name = serializer.validated_data['user']['first_name']
        request.user.email = serializer.validated_data['user']['email']
        request.user.save()
        profile_detail, created = ProfileDetails.objects.get_or_create(user_id=request.user, role_id=4,
                                                                       defaults={'qr_code': user_qrcode()})

        customer.date_of_birth = dob_obj
        customer.user = profile_detail
        customer.gender = serializer.validated_data['profile']['gender']
        if serializer.validated_data['profile']['profession']:
            try:
                profession = Profession.objects.get(name=serializer.validated_data['profile']['profession'])
                customer.profession = profession
            except ObjectDoesNotExist:
                pass
        if serializer.validated_data['profile']['favourite_shop']:
            try:
                shop = Shop.objects.get(name=serializer.validated_data['profile']['favourite_shop'])
                customer.favourite_shop = shop
            except ObjectDoesNotExist:
                pass
        customer.save()

        if customer.date_of_birth:
            earn_points(user=request.user, action='Add DOB and Earn')

        if register_using:
            if register_using == 'google':
                connect_type = 1
                unique_string = request.data.get('unique_string')
            elif register_using == 'facebook':
                connect_type = 0
                unique_string = request.data.get('unique_string')
            CustomerSocialMediaConnection.objects.create(connect_type=connect_type,
                                                         user=request.user,
                                                         unique_string=unique_string
                                                         )
        user = CustomerProfileUserSerializer(request.user)
        profile = CustomerDetailSerializer(customer)
        return Response({'user': user.data, 'profile': profile.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@csrf_exempt
@transaction.atomic
def otp_verification_for_customer_registration(request):
    # message = None
    if request.data['mobile_number'] and request.data['code']:
        otp = get_otp(code=request.data['code'], mobile_number=request.data['mobile_number'])

        if otp:
            if otp.is_active():
                # key = None
                user, created = User.objects.get_or_create(username=request.data['mobile_number'])
                registration = False
                message = 'Logged in'
                role = Group.objects.get(name='Customer')
                try:
                    profile = ProfileDetails.objects.get(user_id=user, role=role)
                    try:
                        CustomerDetail.objects.get(user=profile)
                    except:
                        customer = CustomerDetail.objects.create(user=profile,
                                                                 referral_code=generate_customer_referral_code())
                        message = 'Registration Completed.' + message
                        registration = True

                except ProfileDetails.DoesNotExist:
                    profile = ProfileDetails.objects.create(user_id=user, role=role, qr_code=user_qrcode())
                    user.groups.add(role)
                    user.save()
                    customer = CustomerDetail.objects.create(user=profile,
                                                             referral_code=generate_customer_referral_code())
                    message = 'Registration Completed.' + message
                    registration = True

                customer_id = profile.qr_code

                if registration:
                    refered_obj = CustomerInvite.objects.filter(mobile_number=request.user.username).last()
                    if refered_obj:
                        if earn_referral_points(request.user):
                            customer.is_referred = True
                            customer.referred_code = refered_obj.customer.referral_code
                            customer.save()

                if not user.is_active:
                    user.make_user_active()
                auth_login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                key = token.key
                otp.delete()
                return Response(
                    {'message': message, 'token': key, 'registration': registration, 'customer_id': customer_id},
                    status=status.HTTP_200_OK)

            else:
                message = 'OTP Expired'
        else:
            message = 'Invalid OTP'

    else:
        message = 'Inputs are missing'
    return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)


class CustomerInviteViewSet(generics.ListCreateAPIView):
    '''
    This view is listing all the referred list and create new referral.  
    '''
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    serializer_class = CustomerInviteShortSerializer

    def get_queryset(self):
        '''
        Now it return sms referral list only. 
        '''
        return CustomerInvite.objects.filter(invite_type=0, customer__user__user_id=self.request.user)

    def create(self, request):
        print("user:", self.request.user)
        try:
            customer_obj = CustomerDetail.objects.get(user__user_id=self.request.user)
        except:
            return Response({"status": "0", "message": "Invalid customer."}, status=status.HTTP_401_UNAUTHORIZED)
        CustomerInvite.objects.get_or_create(mobile_number=request.data['mobile_number'],
                                             customer=customer_obj)
        return Response({"status": "1", "message": "Invited successfully."}, status=status.HTTP_200_OK)


class CustomerInformation(generics.RetrieveAPIView):

    def retrieve(self, request, customer_id):
        role = get_object_or_404(Group, name='Customer')
        try:
            user = ProfileDetails.objects.get(qr_code=customer_id, role=role)
        except Exception as e:
            return Response({'status': 0, 'message': 'User is not a customer'}, status=status.HTTP_404_NOT_FOUND)
        user_serializer = UserEditSerializer(user.user_id)
        customer = get_object_or_404(CustomerDetail, user=user)
        return Response({'user': user_serializer.data, }, status=status.HTTP_200_OK)


class RedeemedCouponsViewSet(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        return BurnTransaction.objects.filter(user=self.request.user, status=1, purchased=1, used=0).order_by('-id')

    serializer_class = BurnTransactionDetailSerializer


@csrf_exempt
@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def use_coupon(request, coupon_id):
    try:
        coupon = BurnTransaction.objects.get(user=request.user, id=coupon_id, purchased=1)
    except:
        return Response({'status': 0, 'message': 'You have not purchased the coupon'}, status=status.HTTP_403_FORBIDDEN)
    if check_coupon_expired(coupon):
        return Response({'status': 0, 'message': 'Coupon Expired'}, status=status.HTTP_403_FORBIDDEN)
    coupon.used = True
    return Response(
        {'status': 1, 'message': 'Successfully used the coupon'}, status=status.HTTP_200_OK)


class AboutUsView(APIView):
    '''
    About us page content return.
    '''

    def get(self, request):
        try:
            docu_obj = NhanceDocuments.objects.get(detail_type=0, is_active=True)
        except:
            docu_obj = None
        about_us_content = {}
        if docu_obj:
            about_us_content = NhanceDocumentsSerializer(docu_obj).data
        return Response({'status': 1, 'about_us': about_us_content})
