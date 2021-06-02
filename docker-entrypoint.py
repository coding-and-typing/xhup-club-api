import os
import shlex
import subprocess

"""
Docker 镜像的启动脚本
"""


def main():
    workers = int(os.getenv("WORKERS", 1))

    cmd = f"gunicorn --worker-class=flask_sockets.worker --workers={workers} --bind=:8080 run:app"
    subprocess.run(shlex.split(cmd), check=True)


if __name__ == "__main__":
    main()