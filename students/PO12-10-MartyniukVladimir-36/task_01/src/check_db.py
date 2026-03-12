import sqlite3
import os

db_path = "likes.db"
print(f"Проверка базы данных: {os.path.abspath(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Проверим таблицы
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Таблицы в БД: {tables}")

# Проверим идеи
cursor.execute("SELECT id, title, likes_count FROM ideas;")
ideas = cursor.fetchall()
print(f"Идеи в БД: {ideas}")

# Проверим пользователей
cursor.execute("SELECT id, email FROM users;")
users = cursor.fetchall()
print(f"Пользователи в БД: {users}")

conn.close()
