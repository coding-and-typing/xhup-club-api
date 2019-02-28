### 服务器配置

### 安装 Python

#### 方法一：miniconda

最方便的当然是直接安装 miniconda

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```
Lincence 那里可以直接按 q 退出，然后 yes 就好。
安装完成后，会询问 `Do you wish the installer to initialize Miniconda3
in your /home/ryan/.bashrc ? [yes|no]`，选择 yes. 或者安装后你自己手动配置 miniconda 的 PATH 变量。

2. 在 ryan 的家目录运行：
```bash
git clone git@github.com:ryan4yin/xhup-club-api.git
cd xhup-club-api
pip install -r requirements.txt
```

不知为何，CentOS 上用了 `miniconda` 后，pipenv 生成的虚拟环境，pip 就一直报错 `the ssl module in Python is not available`.
暂时就先用 `requirements.txt` 吧。

2. 将 xhup-club-api 设为 systemd 服务：

```

```

### 自动部署

如果修改了 `.env`，记得运行如下命令更新加密文件：
```bash
tar -cv -f secrets.tar .env id_rsa_for_ssh.key
travis encrypt-file secrets.tar
```
