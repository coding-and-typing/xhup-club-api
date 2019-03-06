import os


# 如果尚未设置环境变量，就先加载环境变量
# 仅开发环境，测试环境不会走这个入口，而生产环境 systemd 会提前使用 .env 设置环境变量
if os.getenv('XHUP_ENV') is None:
    os.environ['XHUP_ENV'] = 'dev'
    os.environ['FLASK_ENV'] = 'development'


from app import create_app, db, socketio
from app.models import MainUser

"""
flask 的启动脚本（入口）
"""

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """在运行 flask shell 时，flask 会自动加载此函数返回的数据"""
    return {'app': app, 'db': db, 'User': MainUser}


if __name__ == '__main__':
    socketio.run(app)  # 使用了 socketio 后，需要通过 socketio.run 函数启动 app
