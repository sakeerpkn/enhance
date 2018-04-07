from django.conf.urls import url

from customer.views import NewsFeedList, user_activity_for_news

urlpatterns = [
    # url(r'^$', NewsFeedList.as_view()),
    # url(r'^user-activity/', user_activity_for_news, name="user_activity_for_news"),

]