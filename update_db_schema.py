import pymysql
from config.settings import settings

# 连接到MySQL数据库
connection = pymysql.connect(
    host=settings.mysql_host,
    user=settings.mysql_user,
    password=settings.mysql_password,
    db=settings.mysql_db,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        # 获取当前表结构
        sql = "DESCRIBE users"
        cursor.execute(sql)
        current_columns = cursor.fetchall()
        current_column_names = [row['Field'] for row in current_columns]
        
        print(f"当前users表列: {current_column_names}")
        
        # 定义要添加的列
        columns_to_add = [
            ("email", "VARCHAR(100)", "UNIQUE NULL DEFAULT NULL"),
            ("level", "VARCHAR(20)", "DEFAULT 'beginner'"),
            ("preferences", "JSON", "NULL"),
            ("created_at", "DATETIME", "DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "DATETIME", "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
        ]
        
        # 添加不存在的列
        for column_name, column_type, column_options in columns_to_add:
            if column_name not in current_column_names:
                sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type} {column_options}"
                print(f"执行SQL: {sql}")
                cursor.execute(sql)
            else:
                print(f"列 {column_name} 已存在，跳过")
    
    # 提交事务
    connection.commit()
    print("\n数据库表结构更新成功")
    
    # 检查更新后的表结构
    with connection.cursor() as cursor:
        sql = "DESCRIBE users"
        cursor.execute(sql)
        result = cursor.fetchall()
        print("\n更新后的users表结构:")
        for row in result:
            print(f"- {row['Field']}: {row['Type']} (Null: {row['Null']}, Key: {row['Key']}, Default: {row['Default']})")
finally:
    connection.close()