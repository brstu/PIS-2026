from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
  id: int
  email: str
  name: str


@dataclass
class Idea:
  id: int
  title: str
  description: str
  author_id: int
  likes_count: int = 0
  status: str = "ACTIVE"

  def add_like(self):
    self.likes_count += 1

  def is_active(self) -> bool:
    return self.status == "ACTIVE"


@dataclass
class Vote:
  id: Optional[int]
  user_id: int
  idea_id: int
  created_at: datetime
