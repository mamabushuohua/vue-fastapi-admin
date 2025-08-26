# FROM node:18.12.0-alpine3.16 AS web
ARG NODE_TAG
FROM node:${NODE_TAG:-22.18.0-alpine3.22} AS web

WORKDIR /tmp
COPY /web ./web
RUN cd /tmp/web && npm i --registry=https://mirrors.tencentyun.com/npm/ && npm run build
# RUN cd /tmp/web && npm i --registry=https://registry.npmmirror.com && npm run build

ARG PYTHON_TAG
FROM python:${PYTHON_TAG:-3.13-slim-bullseye}

WORKDIR /opt/vue-fastapi-admin



RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=core-apt \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=core-apt \
    sed -i "s@http://.*.debian.org@http://mirrors.tencentyun.com@g" /etc/apt/sources.list \
    && rm -f /etc/apt/apt.conf.d/docker-clean \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates gnupg gcc python3-dev bash  vim curl procps net-tools

# 添加 Nginx 官方 GPG 密钥
RUN curl -fsSL https://nginx.org/keys/nginx_signing.key | gpg --dearmor -o /usr/share/keyrings/nginx-archive-keyring.gpg

# 设置官方 APT 源（稳定版）
RUN echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/debian/ bullseye nginx" > /etc/apt/sources.list.d/nginx.list

# 更新 APT 源
RUN apt-get update && apt-get install -y --no-install-recommends nginx && rm -rf /var/lib/apt/lists/*


# 安装依赖
COPY requirements.txt /opt/vue-fastapi-admin/

RUN pip install -r requirements.txt -i https://mirrors.tencentyun.com/pypi/simple

# 拷贝项目文件
COPY app /opt/vue-fastapi-admin/app
COPY run.py /deploy/entrypoint.sh ./

COPY --from=web /tmp/web/dist /opt/vue-fastapi-admin/web/dist
# ADD /deploy/web.conf /etc/nginx/sites-available/web.conf
# RUN rm -f /etc/nginx/sites-enabled/default \ 
#     && ln -s /etc/nginx/sites-available/web.conf /etc/nginx/sites-enabled/

ADD /deploy/web.conf /etc/nginx/conf.d/default.conf


ENV LANG=zh_CN.UTF-8
EXPOSE 80

ENTRYPOINT [ "sh", "entrypoint.sh" ]