from app import create_app, db
from app.models import User

"""
提供给 flask 的启动脚本

需要 `export FLASK_APP=run.py`，然后运行 `flask run` 或 `flask shell` 时，就会从这里进入
"""

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """在运行 flask shell 时，flask 会自动加载此函数返回的数据"""
    return {'app': app, 'db': db, 'User': User}