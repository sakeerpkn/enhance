from django.conf.urls import url

import customer.views as customer_view

urlpatterns = [
    url(r'^shop_categories/$', customer_view.ShopCategoryList.as_view()),
    url(r'^shops/$', customer_view.ShopList.as_view()),
    url(r'^home/$', customer_view.HomeList.as_view()),
    url(r'^shop/(?P<pk>[^/]+)/$', customer_view.ShopRetrieve.as_view()),
    url(r'^coupon/(?P<pk>[^/]+)/$', customer_view.CouponRetrieve.as_view()),
    url(r'^news/$', customer_view.NewsFeedList.as_view()),
    url(r'^news/banner/$', customer_view.NewsFeedBannerList.as_view()),
    url(r'^support/$', customer_view.CustomerQueryView.as_view()),
    url(r'^activity/$', customer_view.user_activity_for_news, name="user_activity_for_news"),
    url(r'^earn-action-detail/$', customer_view.EarnActionDetailList.as_view()),
    url(r'^burn-action-detail/$', customer_view.BurnActionDetailList.as_view()),
    url(r'^summary/$', customer_view.ProfileSummary.as_view()),
    url(r'^earn/$', customer_view.EarnTransactionViewSet.as_view()),
    url(r'^burn/$', customer_view.BurnTransactionViewSet.as_view()),
    url(r'^check_for_recent_coupons/$', customer_view.check_for_recent_coupons, name="check_for_recent_coupons"),
    url(r'^$', customer_view.CustomerRetrieve.as_view()),
    url(r'^edit/(?P<customer_id>[^/]+)/$', customer_view.CustomerRetrieve.as_view()),
    url(r'^update_dob/$', customer_view.update_dob, name="update_dob"),
    url(r'^verify_otp_for_customer/$', customer_view.otp_verification_for_customer_registration,
        name='otp_verification_for_customer_registration'),
    url(r'^add_profile/$', customer_view.AddProfile.as_view()),
    url(r'^invite-friends/$', customer_view.CustomerInviteViewSet.as_view()),
    url(r'^(?P<customer_id>[^/]+)/get_details/$', customer_view.CustomerInformation.as_view()),
    url(r'^redeemed_coupons/$', customer_view.RedeemedCouponsViewSet.as_view()),
    url(r'^use-coupon/(?P<coupon_id>[^/]+)/$', customer_view.use_coupon),
    url(r'^about-us/$', customer_view.AboutUsView.as_view()),
    
    
    

]
