### 服务器配置

### 一、安装 Python

#### 方法一：miniconda

最方便的当然是直接安装 miniconda

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```
Lincence 那里可以直接按 q 退出，然后 yes 就好。
安装完成后，会询问 `Do you wish the installer to initialize Miniconda3
in your /home/ryan/.bashrc ? [yes|no]`，选择 yes. 或者安装后你自己手动配置 miniconda 的 PATH 变量。

### 二. clone 仓库，配置环境：
```bash
git clone git@github.com:ryan4yin/xhup-club-api.git
cd xhup-club-api
pip install -r requirements.txt
```

不知为何，CentOS 上用了 `miniconda` 后，pipenv 生成的虚拟环境，pip 就一直报错 `the ssl module in Python is not available`.
暂时就先用 `requirements.txt` 吧。

### 三、 将 xhup-club-api 设为 systemd 服务：

此处参考了 gunicorn 的官方文档
`/etc/systemd/system/xhup-club-api.service`:
```
[Unit]
Description=xhup-club-api 的 gunicorn 后台
After=network.target

[Service]
PermissionsStartOnly=True
RuntimeDirectory=gunicorn  # 临时文件夹
RuntimeDirectoryMode=0775
PIDFile=/run/gunicorn/xhup-club-api.pid

User=ryan
Group=ryan

EnvironmentFile=/home/ryan/xhup-club-api/.env  # 环境变量
WorkingDirectory=/home/ryan/xhup-club-api  # web app 目录

# unix socket 配置有点麻烦。。先直接用 tcp 吧，nginx 也稍后再配，先跑起来再说
ExecStart=/home/ryan/miniconda3/bin/gunicorn --pid /run/gunicorn/xhup-club-api.pid   \
          --worker-class eventlet -w 1 \
           --bind 0.0.0.0:8000 run:app

ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

然后启动服务：
```bash
sudo systemctl enable xhup-club-api.service
sudo systemctl start xhup-club-api.service
```

要查看服务状态，可以用如下命令：

```bash
sudo systemctl status xhup-club-api.service  # 状态
sudo journalctl -u xhup-club-api.service  # 查看该服务的日志
```

如果修改了 service 文件，需要用 `sudo systemctl daemon-reload` 重载该配置文件。

### 自动部署

如果修改了 `.env`，记得运行如下命令更新加密文件：
```bash
tar -cv -f secrets.tar .env id_rsa_for_ssh.key
travis encrypt-file secrets.tar
```

**NOTE：所有密码一定要同时设为 travis-ci 的环境变量！(变量中的特殊字符 x 要用 \x 转义，否则也会发生不好的事。。)**
这样如果 log 信息中出现了这些变量（比如报错），travis-ci 就会用 [secure] 替换它们！

对 `DB_PASSWORD` 这种使用了 `urllib.parse.quote_plus` 的字符串，quote 后的字符串也应该加进去。

### DB 密码

带特殊字符的 DB_PASSWORD 在 SQLAlchemy 中必须用 `urllib.parse.quote_plus` 编码，
可在 `Alembic` 中如此编码后，会导致错误，必须在 `migrations/env.py` 中做如下修改

```python
# 找到这一句
config.set_main_option('sqlalchemy.url',
                       current_app.config.get('SQLALCHEMY_DATABASE_URI'))

# 用这个替换找到的行
db_url_escaped = current_app.config.get('SQLALCHEMY_DATABASE_URI').replace('%', '%%')
config.set_main_option('sqlalchemy.url', db_url_escaped)
```
