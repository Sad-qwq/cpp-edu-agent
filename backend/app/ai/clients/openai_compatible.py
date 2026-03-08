import json
from typing import Any, Dict, List

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover
    AsyncOpenAI = None

from app.ai.clients.model_provider import ModelProvider


class OpenAICompatibleProvider(ModelProvider):
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model_name: str,
        embedding_model: str | None = None,
        temperature: float = 0.2,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.temperature = temperature
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url) if AsyncOpenAI is not None else None

    @property
    def is_available(self) -> bool:
        return bool(self.api_key and self.model_name and self._client is not None)

    async def generate_json(self, *, system_prompt: str, user_prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        if self._client is None:
            raise RuntimeError("openai package is not installed")

        response = await self._client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"请严格输出 JSON 对象，满足以下结构约束：\n{json.dumps(schema, ensure_ascii=False)}\n\n"
                        f"任务输入：\n{user_prompt}"
                    ),
                },
            ],
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if self._client is None:
            raise RuntimeError("openai package is not installed")

        if not texts:
            return []

        model_name = self.embedding_model or self.model_name
        response = await self._client.embeddings.create(
            model=model_name,
            input=texts,
        )
        return [item.embedding for item in response.data]