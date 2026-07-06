FROM python:3.11-slim-bookworm
LABEL maintainer="mailmzb@163.com"
ENV TZ="Asia/Shanghai"
ENV FLASK_ENV="production"

WORKDIR /usr/src

RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc libc6-dev \
       nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uwsgi -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --timeout 600

RUN apt-get purge -y --auto-remove gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY .nginx /etc/nginx/nginx.conf

COPY . .

CMD supervisord --nodaemon -c supervisord.ini
