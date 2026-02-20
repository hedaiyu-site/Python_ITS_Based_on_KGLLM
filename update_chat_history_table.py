from sqlalchemy import create_engine, text
from config.settings import settings

# 创建数据库引擎
DATABASE_URL = f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_db}"
engine = create_engine(DATABASE_URL)

# 更新chat_history表的content字段长度
def update_chat_history_table():
    """更新chat_history表的content字段长度"""
    with engine.connect() as conn:
        # 检查表是否存在
        result = conn.execute(text("SHOW TABLES LIKE 'chat_history'"))
        if result.fetchone():
            print("表chat_history已存在，开始更新字段长度...")
            
            # 修改content字段长度为10000
            try:
                conn.execute(text("ALTER TABLE chat_history MODIFY COLUMN content VARCHAR(10000) NOT NULL"))
                conn.commit()
                print("成功更新content字段长度为10000字符")
            except Exception as e:
                print(f"更新字段失败: {str(e)}")
                conn.rollback()
        else:
            print("表chat_history不存在，将创建新表...")
            # 创建表
            try:
                conn.execute(text("""
                CREATE TABLE chat_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    message_id VARCHAR(50) NOT NULL UNIQUE,
                    role VARCHAR(20) NOT NULL,
                    content VARCHAR(10000) NOT NULL,
                    response_id VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """))
                conn.commit()
                print("成功创建chat_history表")
            except Exception as e:
                print(f"创建表失败: {str(e)}")
                conn.rollback()
    
    # 检查chat_feedback表是否存在
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES LIKE 'chat_feedback'"))
        if not result.fetchone():
            print("表chat_feedback不存在，将创建新表...")
            # 创建表
            try:
                conn.execute(text("""
                CREATE TABLE chat_feedback (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    response_id VARCHAR(50) NOT NULL,
                    rating INT NOT NULL,
                    comment VARCHAR(500),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """))
                conn.commit()
                print("成功创建chat_feedback表")
            except Exception as e:
                print(f"创建表失败: {str(e)}")
                conn.rollback()

if __name__ == "__main__":
    update_chat_history_table()
