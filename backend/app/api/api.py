
from fastapi import APIRouter
from app.api.endpoints import (
	auth,
	users,
	classes,
	sandbox,
	assignments,
	notifications,
	discussion,
	materials,
	announcements,
	model_config,
	ai_question_generation,
	knowledge_base,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])
api_router.include_router(sandbox.router, prefix="/sandbox", tags=["sandbox"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(discussion.router, prefix="/discussion", tags=["discussion"])
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
api_router.include_router(announcements.router, prefix="/announcements", tags=["announcements"])
api_router.include_router(model_config.router, prefix="/model", tags=["model"])
api_router.include_router(ai_question_generation.router, prefix="/ai", tags=["ai-question-generation"])
api_router.include_router(knowledge_base.router, prefix="/ai/knowledge", tags=["knowledge-base"])
