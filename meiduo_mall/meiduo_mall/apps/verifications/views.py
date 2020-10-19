# Create your views here.
from django.http import HttpResponse
from django.views import View
from django_redis import get_redis_connection
from meiduo_mall.libs.captcha.captcha import captcha


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