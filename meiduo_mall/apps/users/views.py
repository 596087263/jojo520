# Create your views here.
import json
import re

from django import http
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.utils.views import LoginRequiredMixin
from .models import User


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        '''判断用户名是否重复'''
        # 1.查询username在数据库中的个数
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            return http.JsonResponse({'code':400,
                                 'errmsg':'访问数据库失败'})

        # 2.返回结果(json) ---> code & errmsg & count
        return http.JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'count':count})

class MobileCountView(View):

    def get(self, request, mobile):
        '''判断手机号是否重复注册'''
        # 1.查询mobile在mysql中的个数
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            return http.JsonResponse({'code':400,
                                 'errmsg':'查询数据库出错'})

        # 2.返回结果(json)
        return http.JsonResponse({'code':0,
                             'errmsg':'ok',
                             'count':count})


class RegisterView(View):

    def post(self, request):
        '''接收参数, 保存到数据库'''
        # 1.接收参数
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        password2 = dict.get('password2')
        mobile = dict.get('mobile')
        allow = dict.get('allow')
        sms_code_client = dict.get('sms_code')

        # 2.校验(整体)
        if not all([username, password, password2, mobile, allow, sms_code_client]):
            return http.JsonResponse({'code':400,
                                      'errmsg':'缺少必传参数'})

        # 3.username检验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'username格式有误'})

        # 4.password检验
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'password格式有误'})

        # 5.password2 和 password
        if password != password2:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '两次输入不对'})
        # 6.mobile检验
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'mobile格式有误'})
        # 7.allow检验
        if allow != True:
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'allow格式有误'})

        # 8.sms_code检验 (链接redis数据库)
        redis_conn = get_redis_connection('verify_code')

        # 9.从redis中取值
        sms_code_server = redis_conn.get('sms_%s' % mobile)

        # 10.判断该值是否存在
        if not sms_code_server:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '短信验证码过期'})
        # 11.把redis中取得值和前端发的值对比
        if sms_code_client != sms_code_server.decode():
            return http.JsonResponse({'code': 400,
                                      'errmsg': '验证码有误'})

        # 12.保存到数据库 (username password mobile)
        try:
            user =  User.objects.create_user(username=username,
                                             password=password,
                                             mobile=mobile)
        except Exception as e:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '保存到数据库出错'})

        response = http.JsonResponse({'code':0,
                              'errmsg':'ok'})


# 在响应对象中设置用户名信息.
# 将用户名写入到 cookie，有效期 14 天
        response.set_cookie('username',
                    user.username,
                    max_age = 3600 * 24 * 14)

# 返回响应结果
        return response


class LoginView(View):

    def post(self, request):
        '''实现登录接口'''
        # 1.接收参数
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        remembered = dict.get('remembered')


        # 2.校验(整体 + 单个)
        if not all([username, password]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        # 3.验证是否能够登录
        user = authenticate(username=username,
                            password=password)

        # 判断是否为空,如果为空,返回
        if user is None:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '用户名或者密码错误'})

        # 4.状态保持
        login(request, user)

        # 5.判断是否记住用户
        if remembered != True:
            # 7.如果没有记住: 关闭立刻失效
            request.session.set_expiry(0)
        else:
            # 6.如果记住:  设置为两周有效
            request.session.set_expiry(None)

        # 8.返回json
        response = http.JsonResponse({'code': 0,
                                      'errmsg': 'ok'})

        # 在响应对象中设置用户名信息.
        # 将用户名写入到 cookie，有效期 14 天
        response.set_cookie('username',
                            user.username,
                            max_age=3600 * 24 * 14)

        # 返回响应结果
        return response



class LogoutView(View):
    """定义退出登录的接口"""

    def delete(self, request):
        """实现退出登录逻辑"""

        # 清理 session
        logout(request)

        # 创建 response 对象.
        response = http.JsonResponse({'code':0,
                                      'errmsg':'ok'})

        # 调用对象的 delete_cookie 方法, 清除cookie
        response.delete_cookie('username')

        # 返回响应
        return response

class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""
    def get(self, request):
        pass


