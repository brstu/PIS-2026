import sqlite3
import logging

logger = logging.getLogger(__name__)


def init_database(db_path: str = "likes.db"):
  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            author_id INTEGER NOT NULL,
            likes_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ACTIVE',
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            idea_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (idea_id) REFERENCES ideas(id)
        )
    """)

  cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_votes_user_idea
        ON votes(user_id, idea_id)
    """)

  cursor.execute("SELECT COUNT(*) FROM users")
  if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO users (email, name) VALUES (?, ?)",
                   ("alice@example.com", "Alice"))
    cursor.execute("INSERT INTO users (email, name) VALUES (?, ?)",
                   ("bob@example.com", "Bob"))

    cursor.execute("""
            INSERT INTO ideas (title, description, author_id, likes_count)
            VALUES (?, ?, ?, ?)
        """, ("Кулер для воды", "Нужен кулер на 3 этаж", 1, 10))

    cursor.execute("""
            INSERT INTO ideas (title, description, author_id, likes_count)
            VALUES (?, ?, ?, ?)
        """, ("Кофемашина", "Хороший кофе", 2, 5))

  conn.commit()
  conn.close()
  logger.info("Database initialized")
