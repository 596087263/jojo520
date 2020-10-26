from django.urls import re_path, path

from . import views

urlpatterns = [
    # 判断用户名是否重复
    re_path('^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    re_path(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    re_path(r'^register/$', views.RegisterView.as_view()),
    re_path(r'^login/$', views.LoginView.as_view()),
    path('logout', views.LogoutView.as_view()),
    re_path(r'^info/$', views.UserInfoView.as_view()),

]

