import logging
from flask import Flask, request, jsonify, g
from functools import wraps

from domain.exceptions import (
  AlreadyVotedError,
  IdeaNotFoundError,
  IdeaNotActiveError,
  DatabaseError
)
from application.services import LikeService
from infrastructure.repositories import (
  SQLiteVoteRepository,
  SQLiteIdeaRepository,
  SQLiteUnitOfWork
)

logger = logging.getLogger(__name__)


def create_app(db_path: str = "likes.db"):
  app = Flask(__name__)

  def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
      return None
    token = auth_header.split(' ')[1]
    try:
      return int(token)
    except:
      return None

  def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      user_id = get_current_user()
      if not user_id:
        return jsonify({"error": "Требуется авторизация"}), 401
      g.user_id = user_id
      return f(*args, **kwargs)

    return decorated_function

  @app.route('/api/v1/ideas/<int:idea_id>/like', methods=['POST'])
  @login_required
  def like_idea(idea_id):
    uow = SQLiteUnitOfWork(db_path)

    with uow:
      conn = uow.get_connection()
      vote_repo = SQLiteVoteRepository(conn)
      idea_repo = SQLiteIdeaRepository(conn)
      service = LikeService(vote_repo, idea_repo, uow)

      try:
        new_likes = service.like_idea(g.user_id, idea_id)
        return jsonify({"likes": new_likes}), 200
      except IdeaNotFoundError:
        return jsonify({"error": "Идея не найдена"}), 404
      except IdeaNotActiveError:
        return jsonify({"error": "Идея неактивна"}), 400
      except AlreadyVotedError:
        return jsonify({"error": "Вы уже голосовали"}), 409
      except DatabaseError:
        return jsonify({"error": "Сервис временно недоступен"}), 503

  @app.route('/api/v1/ideas/<int:idea_id>', methods=['GET'])
  def get_idea(idea_id):
    uow = SQLiteUnitOfWork(db_path)
    with uow:
      conn = uow.get_connection()
      idea_repo = SQLiteIdeaRepository(conn)
      idea = idea_repo.get_by_id(idea_id)
      if not idea:
        return jsonify({"error": "Идея не найдена"}), 404
      return jsonify({
        "id": idea.id,
        "title": idea.title,
        "description": idea.description,
        "likes": idea.likes_count,
        "status": idea.status
      }), 200

  @app.route('/health', methods=['GET'])
  def health():
    return jsonify({"status": "ok"}), 200

  return app
