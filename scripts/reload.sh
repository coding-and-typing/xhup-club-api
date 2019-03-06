#!/usr/bin/env bash

# 这个脚本用于重启服务器，在服务器上使用
# 需要在项目根目录下运行

git checkout master

# 将 .env 中的 key=value 导入到当前环境变量中，忽略注释行和换行
set -a
. ./prod.env
set +a

pip install -r requirements.txt

# 数据库更新
flask db migrate  # 更新 migrations
flask db upgrade  # 将更新写入数据库

# 重启 gunicorn， -S 选项表示从 stdin 读取密码
# 此 service 的配置文件在 docs/config.md 中
echo $SERVER_PASSWORD | sudo -S systemctl restart xhup-club-api.service
