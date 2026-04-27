from typing import Protocol, Any
from openai import OpenAI
from openai.types.chat import ChatCompletion
from .exceptions import abort

class LLMClient(Protocol):
    """大语言模型客户端通用接口"""
    def chat(self, system_prompt: str, user_prompt: str, response_format: dict[str, Any] | None = None) -> str: # pyright: ignore[reportExplicitAny]
        ...

class OpenAIClient:
    """基于 OpenAI API 的具体实现"""
    def __init__(self, api_key: str, base_url: str, model: str):
        self.model: str = model
        self.client: OpenAI = OpenAI(api_key=api_key, base_url=base_url)

    def chat(self, system_prompt: str, user_prompt: str, response_format: dict[str, Any] | None = None) -> str:   # pyright: ignore[reportExplicitAny]
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        kwargs: dict[str, Any] = {"model": self.model, "messages": messages} # pyright: ignore[reportExplicitAny]
        if response_format:
            kwargs["response_format"] = response_format

        try:
            response: ChatCompletion = self.client.chat.completions.create(**kwargs)  # pyright: ignore[reportUnknownVariableType,reportAny]
            if not isinstance(response, ChatCompletion):
                abort("大语言模型返回类型异常。")
        except Exception as exc:
            abort(f"调用大语言模型 API 失败: {exc}")
            
        content: str | None = response.choices[0].message.content
        
        if not content:
            abort("大语言模型无输出。")
            
        return content
