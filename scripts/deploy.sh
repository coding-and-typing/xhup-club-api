#!/usr/bin/env bash

# 此脚本用于自动部署，在 travis-ci 上使用

# 修改 ssh key 权限，否则 ssh 会报错。
chmod 600 ~/id_rsa_for_ssh.key

mv ~/.env .

# git 路径
GIT_PATH=/usr/local/git/bin/git

# 将配置文件 .env 传到服务器，然后 git pull 更新服务器代码，最后在服务端运行 deploy 脚本。
tar czv .env | ssh ryan@xhup.club -i ~/id_rsa_for_ssh.key \
        -o StrictHostKeyChecking=no \
        "cd ~/xhup-club-api && tar xz && ${GIT_PATH} pull && bash scripts/reload.sh"
