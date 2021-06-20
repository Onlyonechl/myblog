FROM python:3.9-alpine

RUN echo -e http://mirrors.ustc.edu.cn/alpine/v3.9/main/ > /etc/apk/repositories 
  # 使用国内源完全覆盖 /etc/apk/repositories,否则会超时

ENV PYTHONUNBUFFERED 1

RUN apk update \
  # Pillow dependencies
  && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev

WORKDIR /app

RUN pip install pipenv -i https://pypi.douban.com/simple

COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock
RUN pipenv install --system --deploy --ignore-pipfile

# 要注意和线上环境不同的是，我们没有把整个代码 copy 到容器里。线上环境代码一般比较稳定，
# 而对于开发环境，由于需要频繁修改和调试代码，如果我们把代码 copy 到容器，那么容器外做的代码修改，
# 容器内部是无法感知的，这样容器内运行的应用就没法同步我们的修改了。所以我们会把代码通过 Docker 的数据卷来管理。

COPY ./compose/local/django/start.sh /start.sh
RUN sed -i 's/\r//' /start.sh
RUN chmod +x /start.sh