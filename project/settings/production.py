from .common import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['www.onlyone.center', '.onlyone.center']

# elasticsearch 服务的 url 地址是不同的，所以我们在 common 的配置中没有指定 url，在 production.py 设置文件指定之
# HAYSTACK_CONNECTIONS['default']['URL'] = 'http://www.onlyone.center:9200/'
HAYSTACK_CONNECTIONS['default']['URL'] = 'http://elasticsearch:9200/'
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# 配置redis作为缓存服务
CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": "redis://:UJaoRZlNrH40BDaWU6fi@redis:6379/0",
        "OPTIONS": {
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
            "CONNECTION_POOL_CLASS_KWARGS": {"max_connections": 50, "timeout": 20},
            "MAX_CONNECTIONS": 1000,
            "PICKLE_VERSION": -1,
        },
    },
}
