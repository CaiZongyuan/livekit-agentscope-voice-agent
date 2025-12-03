from __future__ import annotations

import asyncio
from dataclasses import dataclass, replace
from typing import Literal
from urllib.parse import urlencode

import httpx

from livekit.agents import (
    APIConnectionError,
    APIConnectOptions,
    APIStatusError,
    APITimeoutError,
    tts,
)
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS, NOT_GIVEN, NotGivenOr
from livekit.agents.utils import aio, is_given

SAMPLE_RATE = 24000
NUM_CHANNELS = 1

DEFAULT_SPEAKER = "忧伤女声.pt"
DEFAULT_VOLUME = 1.0


@dataclass
class _TTSOptions:
    speaker: str
    volume: float
    base_url: str


class TTS(tts.TTS):
    def __init__(
        self,
        *,
        speaker: str = DEFAULT_SPEAKER,
        volume: float = DEFAULT_VOLUME,
        base_url: str = "http://localhost:9880",
    ) -> None:
        """
        创建本地 IndexTTS 1.5 实例。

        参数:
            speaker: 说话人模型文件名，例如 "忧伤女声.pt"
            volume: 音量，默认 1.0
            base_url: TTS 服务地址，默认 "http://localhost:9880"
        """
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),
            sample_rate=SAMPLE_RATE,
            num_channels=NUM_CHANNELS,
        )

        self._opts = _TTSOptions(
            speaker=speaker,
            volume=volume,
            base_url=base_url.rstrip("/"),
        )

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=15.0, read=30.0, write=5.0, pool=5.0),
            follow_redirects=True,
            limits=httpx.Limits(
                max_connections=50, max_keepalive_connections=50, keepalive_expiry=120
            ),
        )

        self._prewarm_task: asyncio.Task | None = None

    @property
    def speaker(self) -> str:
        return self._opts.speaker

    @property
    def provider(self) -> str:
        return "local-indextts"

    def update_options(
        self,
        *,
        speaker: NotGivenOr[str] = NOT_GIVEN,
        volume: NotGivenOr[float] = NOT_GIVEN,
    ) -> None:
        """更新 TTS 配置选项"""
        if is_given(speaker):
            self._opts.speaker = speaker
        if is_given(volume):
            self._opts.volume = volume

    def synthesize(
        self,
        text: str,
        *,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> ChunkedStream:
        return ChunkedStream(tts=self, input_text=text, conn_options=conn_options)

    def prewarm(self) -> None:
        """预热连接"""

        async def _prewarm() -> None:
            try:
                # 发送一个简单的测试请求来预热连接
                params = {
                    "text": "测试",
                    "speaker": self._opts.speaker,
                    "volume": self._opts.volume,
                }
                url = f"{self._opts.base_url}/?{urlencode(params)}"
                await self._client.get(url)
            except Exception:
                pass

        self._prewarm_task = asyncio.create_task(_prewarm())

    async def aclose(self) -> None:
        """关闭资源"""
        if self._prewarm_task:
            await aio.cancel_and_wait(self._prewarm_task)
        await self._client.aclose()


class ChunkedStream(tts.ChunkedStream):
    def __init__(
        self, *, tts: TTS, input_text: str, conn_options: APIConnectOptions
    ) -> None:
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._tts: TTS = tts
        self._opts = replace(tts._opts)

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        """执行 TTS 合成"""
        try:
            # 构建请求 URL
            params = {
                "text": self.input_text,
                "speaker": self._opts.speaker,
                "volume": self._opts.volume,
            }
            url = f"{self._opts.base_url}/?{urlencode(params)}"

            # 发送请求并流式读取响应
            async with self._tts._client.stream(
                "GET",
                url,
                timeout=httpx.Timeout(30, connect=self._conn_options.timeout),
            ) as response:
                # 检查响应状态
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise APIStatusError(
                        message=f"TTS request failed: {error_text.decode('utf-8', errors='ignore')}",
                        status_code=response.status_code,
                        request_id="",
                        body=error_text,
                    )

                # 初始化音频输出
                request_id = response.headers.get("x-request-id", "")
                output_emitter.initialize(
                    request_id=request_id,
                    sample_rate=SAMPLE_RATE,
                    num_channels=NUM_CHANNELS,
                    mime_type="audio/wav",
                )

                # 流式读取音频数据
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    if chunk:
                        output_emitter.push(chunk)

            # 完成输出
            output_emitter.flush()

        except httpx.TimeoutException:
            raise APITimeoutError() from None
        except httpx.HTTPStatusError as e:
            raise APIStatusError(
                message=str(e),
                status_code=e.response.status_code,
                request_id="",
                body=e.response.content,
            ) from None
        except Exception as e:
            raise APIConnectionError() from e
