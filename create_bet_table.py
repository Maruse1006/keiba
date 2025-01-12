import mysql.connector
from mysql.connector import Error

# MySQL 接続情報
DB_CONFIG = {
    "host": "localhost",       # ホスト名
    "user": "root",            # ユーザー名
    "password": "password", # MySQL のパスワード
    "database": "keiba"        # データベース名
}

# マイグレーション SQL
MIGRATION_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    comment TEXT,
    date_info VARCHAR(50) NOT NULL,       -- 日付情報
    location VARCHAR(10) NOT NULL,        -- 場所
    race_number INT NOT NULL,             -- レース番号
    round VARCHAR(20) NOT NULL,           -- 開催回
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);
"""

def run_migrations():
    try:
        # MySQL に接続
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # マイグレーション実行
        for result in cursor.execute(MIGRATION_SQL, multi=True):
            if result.with_rows:
                print(f"Affected Rows: {result.rowcount}")
        connection.commit()

        print("Migrations applied successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    run_migrations()
