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
git https://github.com/coding-and-typing/xhup-club-api.git
cd xhup-club-api
pip install poetry
poetry install
```

### Travis-CI 持续集成/持续部署

首先安装 travis 客户端：

```bash
sudo apt-get install ruby ruby-dev gcc make
gem sources --add https://gems.ruby-china.com/ --remove https://rubygems.org/
sudo gem install travis
travis login --com  # 登录到 com 版的 travis
# 现在才能用 `travis encrypt-file` 命令
```

如果修改了 `prod.env`，记得运行如下命令更新加密文件：
```bash
tar -cv -f secrets.tar prod.env id_rsa_for_ssh.key
travis encrypt-file secrets.tar --com  # # 加 --com，否则默认加到 org 版本
# 将返回信息中的 build script 命令加到 .travis.yaml 中
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


### 域名与协议

域名的话，我想可以找老范讨要个 `typing.xhup.club` 这个子域名
协议必须用 https 和 wss，尤其是 wss，因为 token 不加密完全是明文的。