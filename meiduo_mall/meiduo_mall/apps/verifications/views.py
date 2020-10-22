# Create your views here.
import logging

from django.http import HttpResponse
from django.views import View
from django_redis import get_redis_connection
from meiduo_mall.libs.captcha.captcha import captcha

logger = logging.getLogger('django')
import random
from django import http
from celery_tasks.sms.tasks import ccp_send_sms_code


class ImageCodeView(View):
    '''返回图形验证码的类视图'''

    def get(self, request, uuid):
        '''
        生成图形验证码, 保存到redis中, 另外返回图片
        :param request:请求对象
        :param uuid:浏览器端生成的唯一id
        :return:一个图片
        '''
        # 1.调用工具类 captcha 生成图形验证码
        text, image = captcha.generate_captcha()

        # 2.链接 redis, 获取链接对象
        redis_conn = get_redis_connection('verify_code')

        # 3.利用链接对象, 保存数据到 redis, 使用 setex 函数
        # redis_conn.setex('<key>', '<expire>', '<value>')
        redis_conn.setex('img_%s' % uuid, 300, text)

        # 4.返回(图片)
        return HttpResponse(image,
                            content_type='image/jpg')

class UsernameCountView(View):
    """判断用户名是否重复注册
    GET http://www.meiduo.site:8000/usernames/itcast/count/
    """

    def get(self, request, username):
        """
        查询用户名对应的记录的个数
        :param username: 用户名
        :return: JSON
        """
        try:
            count= User.objects.filter(username=username).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': '400', 'errmsg': '数据错误'})

        return http.JsonResponse({'code': '0', 'errmsg': 'OK', 'count': count})




class SMSCodeView(View):
    def get(self, reqeust, mobile):
        redis_conn = get_redis_connection('verify_code')
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '发送短信过于频繁'})

        image_code_client = reqeust.GET.get('image_code')
        uuid = reqeust.GET.get('image_code_id')

        if not all([image_code_client, uuid]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '图形验证码失效'})

        try:
            redis_conn.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)

        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': 400,
                                      'errmsg': '输入图形验证码有误'})

        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        pl = redis_conn.pipeline()
        pl.setex('sms_code_%s' % mobile, 300, sms_code)
        pl.setex('send_flag_%s' % mobile, 60, 1)
        pl.execute()


        # 原来的写法:
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)

        # 改为现在的写法, 注意: 这里的函数,调用的时候需要加: .delay()
        ccp_send_sms_code.delay(mobile, sms_code)

        return http.JsonResponse({'code': 0,
                                  'errmsg': '发送短信成功'})