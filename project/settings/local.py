from .common import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fbk-%eyzq+bh)$56o2$txpw@i=3p0(#d^w=p*m-%_u6b$a&4#%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['www.onlyone.center', 'onlyone.center','*']

# elasticsearch 服务的 url 地址是不同的，所以我们在 common 的配置中没有指定 url，在 local.py 设置文件指定之：
HAYSTACK_CONNECTIONS['default']['URL'] = 'http://elasticsearch:9200/'
