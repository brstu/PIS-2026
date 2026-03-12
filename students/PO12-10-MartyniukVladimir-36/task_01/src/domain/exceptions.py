class DomainException(Exception):
  """Базовое исключение домена"""
  pass


class AlreadyVotedError(DomainException):
  """Пользователь уже голосовал"""
  pass


class IdeaNotFoundError(DomainException):
  """Идея не найдена"""
  pass


class IdeaNotActiveError(DomainException):
  """Идея неактивна"""
  pass


class DatabaseError(DomainException):
  """Ошибка базы данных"""
  pass
