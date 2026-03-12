import sqlite3
from datetime import datetime
from typing import Optional

from domain.models import Idea, Vote
from domain.exceptions import DatabaseError
from application.interfaces import VoteRepository, IdeaRepository, UnitOfWork


class SQLiteVoteRepository(VoteRepository):
  def __init__(self, connection):
    self.conn = connection

  def exists(self, user_id: int, idea_id: int) -> bool:
    cursor = self.conn.cursor()
    cursor.execute(
      "SELECT id FROM votes WHERE user_id = ? AND idea_id = ?",
      (user_id, idea_id)
    )
    return cursor.fetchone() is not None

  def save(self, user_id: int, idea_id: int) -> Vote:
    cursor = self.conn.cursor()
    now = datetime.now()

    cursor.execute(
      "INSERT INTO votes (user_id, idea_id, created_at) VALUES (?, ?, ?)",
      (user_id, idea_id, now.isoformat())
    )
    vote_id = cursor.lastrowid
    return Vote(id=vote_id, user_id=user_id, idea_id=idea_id, created_at=now)


class SQLiteIdeaRepository(IdeaRepository):
  def __init__(self, connection):
    self.conn = connection

  def get_by_id(self, idea_id: int) -> Optional[Idea]:
    cursor = self.conn.cursor()
    cursor.execute(
      "SELECT id, title, description, author_id, likes_count, status FROM ideas WHERE id = ?",
      (idea_id,)
    )
    row = cursor.fetchone()

    if row:
      return Idea(
        id=row[0],
        title=row[1],
        description=row[2],
        author_id=row[3],
        likes_count=row[4],
        status=row[5]
      )
    return None

  def increment_likes(self, idea_id: int) -> int:
    cursor = self.conn.cursor()
    cursor.execute(
      "UPDATE ideas SET likes_count = likes_count + 1 WHERE id = ?",
      (idea_id,)
    )
    cursor.execute(
      "SELECT likes_count FROM ideas WHERE id = ?",
      (idea_id,)
    )
    result = cursor.fetchone()
    return result[0]

  def get_likes_count(self, idea_id: int) -> int:
    cursor = self.conn.cursor()
    cursor.execute(
      "SELECT likes_count FROM ideas WHERE id = ?",
      (idea_id,)
    )
    result = cursor.fetchone()
    return result[0]


class SQLiteUnitOfWork(UnitOfWork):
  def __init__(self, db_path: str):
    self.db_path = db_path
    self.connection = None
    self._depth = 0

  def __enter__(self):
    if self._depth == 0:
      self.connection = sqlite3.connect(self.db_path)
    self._depth += 1
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self._depth -= 1
    if self._depth == 0:
      if exc_type is None:
        self.connection.commit()
      else:
        self.connection.rollback()
      self.connection.close()
      self.connection = None

  def commit(self):
    if self.connection:
      self.connection.commit()

  def rollback(self):
    if self.connection:
      self.connection.rollback()

  def get_connection(self):
    return self.connection
