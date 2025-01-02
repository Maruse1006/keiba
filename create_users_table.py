import pymysql

# MySQLに接続
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='password',  # 事前に設定したパスワード
    database='keiba'
)
cursor = conn.cursor()

# ユーザーテーブルを作成
create_table_query = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
cursor.execute(create_table_query)

print("Users table created successfully.")

# データベース変更を保存して接続を閉じる
conn.commit()
conn.close()
