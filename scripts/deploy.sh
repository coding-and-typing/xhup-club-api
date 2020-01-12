#!/usr/bin/env bash

# 此脚本用于自动部署，在 travis-ci 上使用
chmod 600 id_rsa_for_ssh.key

# 通过 rsync 将当前文件夹同步到部署服务器上，不删除服务器上多出来的文件。
rsync --quiet --recursive \
    -e "ssh -i id_rsa_for_ssh.key" \
    $HOME/deploy-scripts ryan@xhup.club:xhup-club-api

ssh ryan@xhup.club -i id_rsa_for_ssh.key \
    "cd xhup-club-api && docker-compose pull && docker-compose up -d"
