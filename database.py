import pandas as pd
import random
from sqlalchemy import create_engine
import pymysql

# 配置資料庫連接
DATABASE_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'Quiz',
    'port': 3306
}

# 讀取並重命名測驗數據
quiz = pd.read_csv('quiz1.csv', encoding="utf-8")

quiz.rename(columns={'題目編號': 'NUM', 
                     '題目': 'QUESTION', 
                     '答題選項1': 'SELECTION_1',
                     '答題選項2': 'SELECTION_2', 
                     '答題選項3': 'SELECTION_3', 
                     '答題選項4': 'SELECTION_4',
                     '答案編號': 'ANSWER'}, 
            inplace=True)

def initialize_database():
    # 連接到 MySQL 伺服器
    connection = pymysql.connect(
        host=DATABASE_CONFIG['host'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password'],
        port=DATABASE_CONFIG['port']
    )
    cursor = connection.cursor()

    # 創建資料庫
    cursor.execute("CREATE DATABASE IF NOT EXISTS Quiz")
    print("資料庫建立成功")

    # 使用資料庫
    cursor.execute("USE Quiz")

    # 創建資料表
    cursor.execute('''CREATE TABLE IF NOT EXISTS quiz (
                        NUM INT PRIMARY KEY,
                        QUESTION TEXT,
                        SELECTION_1 TEXT,
                        SELECTION_2 TEXT,
                        SELECTION_3 TEXT,
                        SELECTION_4 TEXT,
                        ANSWER INT
                      )
                   ''')
    print("資料表已建立成功")

    # 檢查表格是否為空
    cursor.execute("SELECT COUNT(*) FROM quiz")
    result = cursor.fetchone()
    if result[0] == 0:
        engine = create_engine(f'mysql+pymysql://{DATABASE_CONFIG["user"]}:{DATABASE_CONFIG["password"]}@{DATABASE_CONFIG["host"]}:{DATABASE_CONFIG["port"]}/{DATABASE_CONFIG["database"]}')
        quiz.to_sql('quiz', engine, if_exists='append', index=False)
        print("資料已成功儲存至資料庫")
    else:
        print("資料庫中已存在資料")

    # 關閉連接
    connection.close()
    print("MySQL 連接已關閉")

def update_database():
    connection = pymysql.connect(
        host=DATABASE_CONFIG['host'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password'],
        port=DATABASE_CONFIG['port'],
        database=DATABASE_CONFIG['database']
    )
    cursor = connection.cursor()

    engine = create_engine(f'mysql+pymysql://{DATABASE_CONFIG["user"]}:{DATABASE_CONFIG["password"]}@{DATABASE_CONFIG["host"]}:{DATABASE_CONFIG["port"]}/{DATABASE_CONFIG["database"]}')
    quiz.to_sql('quiz', engine, if_exists='replace', index=False)
    print("資料已成功更新至資料庫")

    connection.close()
    print("MySQL 連接已關閉")

def get_db_connection():
    connection = pymysql.connect(
        host=DATABASE_CONFIG['host'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password'],
        database=DATABASE_CONFIG['database'],
        port=DATABASE_CONFIG['port']
    )
    return connection

def generate_quiz():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT NUM FROM quiz")
    all_nums = [row[0] for row in cursor.fetchall()]
    
    random_nums = random.sample(all_nums, min(5, len(all_nums)))
    
    questions = []
    for num in random_nums:
        cursor.execute('''SELECT * 
                          FROM quiz 
                          WHERE NUM = %s''', (num,))
        question = cursor.fetchone()
        if question:
            questions.append(question)
    
    connection.close()
    
    return questions

#更新資料庫
# initialize_database()

