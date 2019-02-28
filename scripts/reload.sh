#!/usr/bin/env bash

# 这个脚本用于重启服务器，在服务器上使用
# 需要在项目根目录下运行

source .env

pip install -r requirements.txt

# 数据库更新
flask db upgrade

# 重启 gunicorn， -S 选项表示从 stdin 读取密码
# 此 service 的配置文件在 docs/config.md 中
echo $SERVER_PASSWORD | sudo -S systemctl reload xhup-club-api.service
