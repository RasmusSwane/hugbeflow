import re
import threading
import time
from typing import Any, AsyncIterator, Sequence

from langchain_openai import ChatOpenAI


def parse_nvidia_api_keys(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, (list, tuple, set)):
        return [str(k).strip() for k in raw if str(k).strip()]
    return [part.strip() for part in re.split(r"[\n,]", str(raw)) if part.strip()]


def _is_rate_limit_error(exc: Exception) -> bool:
    if getattr(exc, "status_code", None) == 429:
        return True
    response = getattr(exc, "response", None)
    if response is not None and getattr(response, "status_code", None) == 429:
        return True
    message = str(exc).lower()
    return "rate limit" in message or "too many requests" in message or "429" in message


class _ApiKeyRotator:
    def __init__(self, keys: Sequence[str], cooldown_seconds: int = 60):
        self.keys = list(keys)
        self.cooldown_seconds = max(1, int(cooldown_seconds))
        self._cursor = 0
        self._cooldown_until: dict[str, float] = {}
        self._lock = threading.Lock()

    def next_key(self) -> str | None:
        now = time.monotonic()
        with self._lock:
            for _ in range(len(self.keys)):
                index = self._cursor % len(self.keys)
                self._cursor += 1
                key = self.keys[index]
                if self._cooldown_until.get(key, 0.0) <= now:
                    return key
        return None

    def mark_rate_limited(self, key: str) -> None:
        with self._lock:
            self._cooldown_until[key] = time.monotonic() + self.cooldown_seconds


class RotatingNvidiaChatOpenAI(ChatOpenAI):
    def __init__(self, **kwargs: Any):
        raw_keys = kwargs.pop("nvidia_api_keys", None)
        cooldown_seconds = kwargs.pop("nvidia_key_cooldown_seconds", 60)
        kwargs.pop("nvidia_provider_api", None)
        kwargs.pop("nvidia_model", None)

        keys = parse_nvidia_api_keys(raw_keys)
        fallback_key = kwargs.get("api_key") or kwargs.get("openai_api_key")
        if fallback_key and not keys:
            keys = [str(fallback_key)]
        if not keys:
            raise ValueError("NVIDIA provider requires at least one API key")

        kwargs.setdefault("api_key", keys[0])
        kwargs.setdefault("max_retries", 0)
        delegate_kwargs = dict(kwargs)
        super().__init__(**kwargs)

        object.__setattr__(self, "_nvidia_rotator", _ApiKeyRotator(keys, int(cooldown_seconds)))
        object.__setattr__(self, "_delegate_kwargs", delegate_kwargs)

    def _call_with_rotation(self, call_factory):
        last_rate_limit_error = None
        for _ in range(len(self._nvidia_rotator.keys)):
            key = self._nvidia_rotator.next_key()
            if key is None:
                break

            model_kwargs = dict(self._delegate_kwargs)
            model_kwargs["api_key"] = key
            delegate = ChatOpenAI(**model_kwargs)
            try:
                return call_factory(delegate)
            except Exception as exc:  # noqa: BLE001
                if _is_rate_limit_error(exc):
                    self._nvidia_rotator.mark_rate_limited(key)
                    last_rate_limit_error = exc
                    continue
                raise

        raise RuntimeError(
            "All NVIDIA API keys are currently rate-limited or cooling down"
        ) from last_rate_limit_error

    async def _acall_with_rotation(self, call_factory):
        last_rate_limit_error = None
        for _ in range(len(self._nvidia_rotator.keys)):
            key = self._nvidia_rotator.next_key()
            if key is None:
                break

            model_kwargs = dict(self._delegate_kwargs)
            model_kwargs["api_key"] = key
            delegate = ChatOpenAI(**model_kwargs)
            try:
                return await call_factory(delegate)
            except Exception as exc:  # noqa: BLE001
                if _is_rate_limit_error(exc):
                    self._nvidia_rotator.mark_rate_limited(key)
                    last_rate_limit_error = exc
                    continue
                raise

        raise RuntimeError(
            "All NVIDIA API keys are currently rate-limited or cooling down"
        ) from last_rate_limit_error

    def _generate(self, messages: list[Any], stop: list[str] | None = None, run_manager: Any = None, **kwargs: Any):
        return self._call_with_rotation(
            lambda delegate: delegate._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
        )

    async def _agenerate(self, messages: list[Any], stop: list[str] | None = None, run_manager: Any = None, **kwargs: Any):
        return await self._acall_with_rotation(
            lambda delegate: delegate._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
        )

    def _stream(self, messages: list[Any], stop: list[str] | None = None, run_manager: Any = None, **kwargs: Any):
        return self._call_with_rotation(
            lambda delegate: delegate._stream(messages, stop=stop, run_manager=run_manager, **kwargs)
        )

    async def _astream(
        self,
        messages: list[Any],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> AsyncIterator[Any]:
        stream = await self._acall_with_rotation(
            lambda delegate: delegate._astream(messages, stop=stop, run_manager=run_manager, **kwargs)
        )
        async for chunk in stream:
            yield chunk
