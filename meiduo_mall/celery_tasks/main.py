from celery import Celery


# 利用导入的 Celery 创建对象

celery_app = Celery('meiduo')

# 将刚刚的 config 配置给 celery
# 里面的参数为我们创建的 config 配置文件:
celery_app.config_from_object('celery_tasks.config')
celery_app.autodiscover_tasks(['celery_tasks.sms'])