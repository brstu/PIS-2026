import logging
import sys
from api.routes import create_app
from infrastructure.database import init_database

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    logging.StreamHandler(sys.stdout)
  ]
)

logger = logging.getLogger(__name__)


def main():
  logger.info("Starting Like Service")

  try:
    init_database()
    logger.info("Database initialized")
  except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    sys.exit(1)

  app = create_app()
  logger.info("Starting Flask server on http://localhost:5000")
  app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
  main()
