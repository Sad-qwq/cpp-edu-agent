from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.clients.model_provider import ModelProvider
from app.ai.clients.openai_compatible import OpenAICompatibleProvider
from app.core.config import settings
from app.models.model_config import ModelConfig


async def get_model_provider(session: AsyncSession) -> Optional[ModelProvider]:
    if not settings.AI_ENABLE_REMOTE_GENERATION or not settings.AI_API_KEY:
        return None

    model_config = await session.get(ModelConfig, 1)
    if not model_config:
        model_config = ModelConfig()
        session.add(model_config)
        await session.commit()
        await session.refresh(model_config)

    model_name = settings.AI_MODEL_NAME or model_config.model_name
    embedding_model = settings.AI_EMBEDDING_MODEL or None

    provider = OpenAICompatibleProvider(
        base_url=settings.AI_BASE_URL,
        api_key=settings.AI_API_KEY,
        model_name=model_name,
        embedding_model=embedding_model,
        temperature=model_config.temperature,
    )
    return provider if provider.is_available else None