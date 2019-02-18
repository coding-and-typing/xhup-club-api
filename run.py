from app import create_app, db
from app.models import User

"""
提供给 `flask shell` 的启动脚本
"""

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}
