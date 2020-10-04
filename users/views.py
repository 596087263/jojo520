from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django import http
def register(request):
    return http.HttpResponse('这里假装返回注册页面')
