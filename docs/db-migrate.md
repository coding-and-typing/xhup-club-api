### 数据库迁移

项目使用 flask-migrate 自动从 SQLAlchemy 的 Model 生成数据库对应的表。
并且在 Model 发生改变时，可以通过 flask-migrate 自动检测更改，然后将更改应用到数据库表上。

```bash
# 1. flask-migrate 初始化
flask db init

# 2. 初始化生成的 migrations/env.py 不能直接使用，需要更改
# 这一步详见 config.md

# 3. 每次 model 更改后，运行此命令(如果提示数据库不是最新，就先 upgrade)
flask db migrate  # 这会自动检测 model 的更改

# 4. 将 migrate 检测到的更新应用到数据库
flask db upgrade
```

**NOTE**：`flask db migrate` 存在如下缺陷：
1. 不能正确检测表名的更改
    - 这会被检测成删除掉原有的表，然后新建修改后的表
    - 因此在生产环境，一定要手动修改生成的代码！！！
1. 不能正确检测列名的更改
    - 同上，你需要手动修改生成的 migrations/versions/xxxx.py
1. 不能检测到匿名约束（Anonymously named constraints）
    - 因此你一定要为每个 constraints 命名，例如：`UniqueConstraint('col1', 'col2', name="my_name")`
1. 不能检测到后端数据库不支持的特殊数据类型，比如枚举 `ENUM`


详见 [what-does-autogenerate-detect-and-what-does-it-not-detect](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)




