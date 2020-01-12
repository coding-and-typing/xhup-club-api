FROM python:3.7-alpine

LABEL maintainer="ryan4yin <xiaoyin_c@qq.com>"

COPY . /xhup-club-api

WORKDIR /xhup-club-api

# RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories
RUN apk --no-cache add \
        build-base \
        openssl-dev \
        libffi-dev \
        zlib-dev \
        jpeg-dev \
        libxslt-dev

# pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
RUN pip install poetry gunicorn \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev \
    && pip uninstall poetry --yes \
    && rm -rf ~/.cache

ENTRYPOINT ["python", "docker-entrypoint.py"]

EXPOSE 8080
