import os

# 如果尚未设置环境变量，就先加载环境变量
# 仅开发环境，测试环境不会走这个入口，而生产环境 systemd 会提前使用 .env 设置环境变量
if os.getenv('XHUP_ENV') is None:
    os.environ['XHUP_ENV'] = 'dev'
    os.environ['FLASK_ENV'] = 'development'

from app import create_app, db, redis
from app.models import MainUser

"""
flask 的启动脚本（入口）

Note: 因为使用了 flask 的开发服务器无法提供 websocket 服务，
    因此不能直接通过 `flask run` 命令启动服务器！那样的话 ws api 会不可用！
"""

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """在运行 flask shell 时，flask 会自动加载此函数返回的数据"""
    return {
        'app': app,
        'db': db,
        'User': MainUser,
        'redis': redis
    }


if __name__ == '__main__':
    # 需要使用 geventwebsocket 提供 websocket 服务，因此不能用常规方式（app.run）启动服务器
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('', 6543),
                               app,
                               handler_class=WebSocketHandler)
    server.serve_forever()
