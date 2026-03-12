from abc import ABC, abstractmethod
from typing import Optional
from domain.models import Idea, Vote


class VoteRepository(ABC):
  @abstractmethod
  def exists(self, user_id: int, idea_id: int) -> bool:
    pass

  @abstractmethod
  def save(self, user_id: int, idea_id: int) -> Vote:
    pass


class IdeaRepository(ABC):
  @abstractmethod
  def get_by_id(self, idea_id: int) -> Optional[Idea]:
    pass

  @abstractmethod
  def increment_likes(self, idea_id: int) -> int:
    pass

  @abstractmethod
  def get_likes_count(self, idea_id: int) -> int:
    pass


class UnitOfWork(ABC):
  @abstractmethod
  def __enter__(self):
    pass

  @abstractmethod
  def __exit__(self, exc_type, exc_val, exc_tb):
    pass

  @abstractmethod
  def commit(self):
    pass

  @abstractmethod
  def rollback(self):
    pass
