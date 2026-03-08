from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ModelProvider(ABC):
    @abstractmethod
    async def generate_json(self, *, system_prompt: str, user_prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError