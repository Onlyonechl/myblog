FROM nginx:1.17.1

# 替换为国内源
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak
COPY ./compose/production/nginx/sources.list /etc/apt/
RUN apt-get update && apt-get install -y --allow-unauthenticated certbot python-certbot-nginx

# RUN apt-get update && apt-get install snapd && systemctl enable --now snapd.socket \
# && ln -s /var/lib/snapd/snap /snap && snap install core && snap refresh core && snap install --classic certbot \
# && ln -s /snap/bin/certbot /usr/bin/certbot

RUN rm /etc/nginx/conf.d/default.conf
COPY ./compose/production/nginx/myblog.conf /etc/nginx/conf.d/myblog.conf


