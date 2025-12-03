from __future__ import annotations

import asyncio
import base64
import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import aiohttp
import httpx

from livekit import rtc
from livekit.agents import (
    DEFAULT_API_CONNECT_OPTIONS,
    APIConnectionError,
    APIConnectOptions,
    APIStatusError,
    APITimeoutError,
    stt,
    utils,
)
from livekit.agents.types import (
    NOT_GIVEN,
    NotGivenOr,
)
from livekit.agents.utils import AudioBuffer, is_given

# 采样率配置
SAMPLE_RATE = 16000  # Qwen3-ASR 通常使用 16kHz
NUM_CHANNELS = 1


@dataclass
class _STTOptions:
    model: str
    language: str
    enable_itn: bool
    prompt: str


class STT(stt.STT):
    def __init__(
        self,
        *,
        model: str = "qwen3-asr-flash",
        language: str = "zh",
        enable_itn: bool = True,
        prompt: str = "",
        api_key: NotGivenOr[str] = NOT_GIVEN,
        base_url: str = "https://dashscope.aliyuncs.com",
        client: httpx.AsyncClient | None = None,
    ):
        """
        创建 Qwen3-ASR STT 实例。

        Args:
            model: 使用的模型名称，默认 "qwen3-asr-flash"
            language: 语言代码（如 "zh", "en"）
            enable_itn: 是否启用逆文本规范化（数字、日期等转换）
            prompt: 可选的提示文本
            api_key: DashScope API Key，如不提供则从环境变量 DASHSCOPE_API_KEY 读取
            base_url: API 基础 URL，默认北京地域
            client: 可选的预配置 httpx.AsyncClient
        """
        super().__init__(
            capabilities=stt.STTCapabilities(streaming=False, interim_results=False)
        )

        # 获取 API Key
        self._api_key = (
            api_key if is_given(api_key) else os.environ.get("DASHSCOPE_API_KEY")
        )
        if not self._api_key:
            raise ValueError(
                "DASHSCOPE_API_KEY is required. Set it via api_key parameter or DASHSCOPE_API_KEY environment variable"
            )

        self._base_url = base_url.rstrip("/")
        self._opts = _STTOptions(
            model=model,
            language=language,
            enable_itn=enable_itn,
            prompt=prompt,
        )

        self._client = client or httpx.AsyncClient(
            timeout=httpx.Timeout(connect=15.0, read=30.0, write=5.0, pool=5.0),
            follow_redirects=True,
            limits=httpx.Limits(
                max_connections=50,
                max_keepalive_connections=50,
                keepalive_expiry=120,
            ),
        )

    @property
    def model(self) -> str:
        return self._opts.model

    @property
    def provider(self) -> str:
        return "dashscope"

    @staticmethod
    def with_singapore(
        *,
        model: str = "qwen3-asr-flash",
        language: str = "zh",
        enable_itn: bool = True,
        prompt: str = "",
        api_key: NotGivenOr[str] = NOT_GIVEN,
        client: httpx.AsyncClient | None = None,
    ) -> STT:
        """
        创建新加坡地域的 Qwen3-ASR STT 实例。
        注意：新加坡和北京地域的 API Key 不同。
        """
        return STT(
            model=model,
            language=language,
            enable_itn=enable_itn,
            prompt=prompt,
            api_key=api_key,
            base_url="https://dashscope-intl.aliyuncs.com",
            client=client,
        )

    def update_options(
        self,
        *,
        model: NotGivenOr[str] = NOT_GIVEN,
        language: NotGivenOr[str] = NOT_GIVEN,
        enable_itn: NotGivenOr[bool] = NOT_GIVEN,
        prompt: NotGivenOr[str] = NOT_GIVEN,
    ) -> None:
        """更新 STT 选项"""
        if is_given(model):
            self._opts.model = model
        if is_given(language):
            self._opts.language = language
        if is_given(enable_itn):
            self._opts.enable_itn = enable_itn
        if is_given(prompt):
            self._opts.prompt = prompt

    async def _recognize_impl(
        self,
        buffer: AudioBuffer,
        *,
        language: NotGivenOr[str] = NOT_GIVEN,
        conn_options: APIConnectOptions,
    ) -> stt.SpeechEvent:
        """实现语音识别"""
        try:
            # 合并音频帧并转换为 base64
            combined_frame = rtc.combine_audio_frames(buffer)
            audio_data = combined_frame.data.tobytes()
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")

            # 构建请求
            url = urljoin(
                self._base_url, "/api/v1/services/aigc/multimodal-generation/generation"
            )

            current_language = language if is_given(language) else self._opts.language

            payload = {
                "model": self._opts.model,
                "input": {
                    "messages": [
                        {
                            "content": [{"text": self._opts.prompt}],
                            "role": "system",
                        },
                        {
                            "content": [
                                {
                                    "audio": f"data:audio/pcm;rate={SAMPLE_RATE};base64,{audio_base64}"
                                }
                            ],
                            "role": "user",
                        },
                    ]
                },
                "parameters": {
                    "asr_options": {
                        "enable_itn": self._opts.enable_itn,
                    }
                },
            }

            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }

            # 发送请求
            response = await self._client.post(
                url,
                json=payload,
                headers=headers,
                timeout=httpx.Timeout(
                    conn_options.timeout, connect=conn_options.timeout
                ),
            )

            if response.status_code != 200:
                raise APIStatusError(
                    message=f"Qwen3-ASR API error: {response.text}",
                    status_code=response.status_code,
                    request_id=response.headers.get("X-Request-Id", ""),
                    body=response.text,
                )

            result = response.json()

            # 解析响应
            text = ""
            if "output" in result and "choices" in result["output"]:
                choices = result["output"]["choices"]
                if choices and len(choices) > 0:
                    message = choices[0].get("message", {})
                    content = message.get("content", [])
                    if content and len(content) > 0:
                        text = content[0].get("text", "")

            return stt.SpeechEvent(
                type=stt.SpeechEventType.FINAL_TRANSCRIPT,
                alternatives=[
                    stt.SpeechData(
                        text=text,
                        language=current_language,
                    )
                ],
            )

        except httpx.TimeoutException:
            raise APITimeoutError() from None
        except httpx.HTTPStatusError as e:
            raise APIStatusError(
                message=str(e),
                status_code=e.response.status_code,
                request_id=e.response.headers.get("X-Request-Id", ""),
                body=e.response.text,
            ) from None
        except Exception as e:
            raise APIConnectionError() from e

    async def aclose(self) -> None:
        """关闭客户端"""
        await self._client.aclose()
