from sqlalchemy import create_engine, inspect
from config.settings import settings

# 创建SQLAlchemy引擎
DATABASE_URL = f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_db}"
engine = create_engine(DATABASE_URL)

# 使用inspect检查数据库结构
inspector = inspect(engine)

# 列出所有表
print("数据库中的表:")
tables = inspector.get_table_names()
print(tables)

# 如果users表存在，检查其结构
if 'users' in tables:
    print("\nusers表结构:")
    columns = inspector.get_columns('users')
    for column in columns:
        print(f"- {column['name']}: {column['type']}")
else:
    print("\nusers表不存在")