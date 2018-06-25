# _*_ coding:utf-8 _*_

from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^users/$', views.UserView.as_view()),
    url(r'^authorizations/$',obtain_jwt_token),   #登录认证
    url(r'^user/$',views.UserDetailView.as_view()),  #个人中心基本信息
    url(r'^email/$',views.EmailView.as_view()),  #邮箱验证
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),

]