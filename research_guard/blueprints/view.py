from sanic import Blueprint

from research_guard.blueprints.ai.view import ai_bp
from research_guard.blueprints.research.view import research_bp
from research_guard.blueprints.security.view import security_bp

api_models = [
    "research_guard.blueprints.research.models",
    "sanic_security.models",
]

api = Blueprint.group(
    security_bp,
    research_bp,
    ai_bp,
    version=1,
    version_prefix="/api/v",
)
