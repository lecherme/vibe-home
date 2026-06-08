from typing import Any

from app.core.config import get_settings

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover
    Anthropic = None  # type: ignore[assignment]

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment]


def _complete_with_anthropic(prompt: str, max_tokens: int, temperature: float) -> str:
    settings = get_settings()
    if not settings.llm_api_key:
        raise RuntimeError("LLM_API_KEY is not configured")
    if Anthropic is None:
        raise RuntimeError("anthropic package is not installed")

    response = Anthropic(api_key=settings.llm_api_key).messages.create(
        model=settings.llm_model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    blocks = getattr(response, "content", [])
    content = "\n".join(block.text for block in blocks if hasattr(block, "text") and block.text)
    return content.strip()


def _extract_openai_content(response: Any) -> str:
    choices = getattr(response, "choices", [])
    if not choices:
        return ""

    message = getattr(choices[0], "message", None)
    if message is None:
        return ""

    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        text_parts = []
        for item in content:
            text_value = getattr(item, "text", None)
            if text_value:
                text_parts.append(text_value)
            elif isinstance(item, dict) and item.get("type") == "text" and item.get("text"):
                text_parts.append(str(item["text"]))
        return "\n".join(text_parts).strip()
    return ""


def _complete_with_openai(
    prompt: str,
    max_tokens: int,
    temperature: float,
    *,
    base_url: str | None = None,
) -> str:
    settings = get_settings()
    if not settings.llm_api_key:
        raise RuntimeError("LLM_API_KEY is not configured")
    if OpenAI is None:
        raise RuntimeError("openai package is not installed")

    client = OpenAI(api_key=settings.llm_api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return _extract_openai_content(response)


def complete(prompt: str, max_tokens: int, temperature: float) -> str:
    settings = get_settings()

    if settings.llm_provider == "anthropic":
        return _complete_with_anthropic(prompt, max_tokens, temperature)

    if settings.llm_provider == "openai":
        return _complete_with_openai(prompt, max_tokens, temperature)

    if settings.llm_provider == "openai_compatible":
        if not settings.llm_base_url:
            raise RuntimeError("LLM_BASE_URL is required for openai_compatible provider")
        return _complete_with_openai(
            prompt,
            max_tokens,
            temperature,
            base_url=settings.llm_base_url,
        )

    raise RuntimeError(f"Unsupported LLM provider: {settings.llm_provider}")
