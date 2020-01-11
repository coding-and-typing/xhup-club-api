FROM python:3.7-alpine

LABEL maintainer="xiaoyin_c@qq.com"

COPY . /xhup-club-api

WORKDIR /xhup-club-api

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
    && apk --no-cache add \
        build-base \
        openssl-dev \
        libffi-dev \
        zlib-dev \
        jpeg-dev \
        libxslt-dev

RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ poetry gunicorn \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev \
    && rm -rf ~/.cache

ENTRYPOINT ["python", "docker-entrypoint.py"]

EXPOSE 8080
