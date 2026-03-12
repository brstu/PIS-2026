import logging
from domain.exceptions import (
  AlreadyVotedError,
  IdeaNotFoundError,
  IdeaNotActiveError,
  DatabaseError
)
from application.interfaces import VoteRepository, IdeaRepository, UnitOfWork

logger = logging.getLogger(__name__)


class LikeService:
  def __init__(
    self,
    vote_repo: VoteRepository,
    idea_repo: IdeaRepository,
    uow: UnitOfWork
  ):
    self.vote_repo = vote_repo
    self.idea_repo = idea_repo
    self.uow = uow

  def like_idea(self, user_id: int, idea_id: int) -> int:
    idea = self.idea_repo.get_by_id(idea_id)
    if not idea:
      logger.warning(f"Idea {idea_id} not found")
      raise IdeaNotFoundError(f"Idea with id {idea_id} not found")

    if not idea.is_active():
      logger.warning(f"Idea {idea_id} is not active")
      raise IdeaNotActiveError(f"Idea {idea_id} is deleted")

    if self.vote_repo.exists(user_id, idea_id):
      logger.info(f"User {user_id} already voted for idea {idea_id}")
      raise AlreadyVotedError(f"User already voted")

    try:
      with self.uow:
        self.vote_repo.save(user_id, idea_id)
        new_likes = self.idea_repo.increment_likes(idea_id)
        logger.info(f"Like added: user={user_id}, idea={idea_id}, new_likes={new_likes}")
        return new_likes
    except Exception as e:
      logger.error(f"Database error: {str(e)}")
      raise DatabaseError(f"Failed to add like: {str(e)}")
