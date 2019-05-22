from app import db

"""
拆五笔赛文系统账号，用于将赛文同步到该系统上
"""


class ChaiWuBiUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128), nullable=False)  # 拆五笔要求明文。。

    # 账号所有者（级联）
    main_user_id = db.Column(db.Integer,
                             db.ForeignKey('main_user.id', ondelete="CASCADE", onupdate="CASCADE"),
                             index=True, nullable=False)


