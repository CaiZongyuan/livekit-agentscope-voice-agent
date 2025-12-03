from __future__ import annotations

import asyncio
from dataclasses import dataclass, replace
from typing import Literal, Union

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

RESPONSE_FORMATS = Union[Literal["mp3", "opus", "aac", "flac", "wav", "pcm"], str]


@dataclass
class _TTSOptions:
    voice: str
    response_format: RESPONSE_FORMATS


class IndexTTS(tts.TTS):
    def __init__(
        self,
        *,
        base_url: str = "http://localhost:6006",
        voice: str = "default",
        response_format: NotGivenOr[RESPONSE_FORMATS] = NOT_GIVEN,
        timeout: float = 30.0,
    ) -> None:
        """
        创建本地 TTS 服务的实例

        Args:
            base_url: TTS 服务的基础 URL
            voice: 使用的音色/角色名称
            response_format: 音频格式
            timeout: 请求超时时间
        """
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),
            sample_rate=SAMPLE_RATE,
            num_channels=NUM_CHANNELS,
        )

        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

        self._opts = _TTSOptions(
            voice=voice,
            response_format=response_format if is_given(response_format) else "wav",
        )

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=15.0, read=timeout, write=5.0, pool=5.0),
            follow_redirects=True,
            limits=httpx.Limits(
                max_connections=50, max_keepalive_connections=50, keepalive_expiry=120
            ),
        )

        self._prewarm_task: asyncio.Task | None = None

    @property
    def voice(self) -> str:
        return self._opts.voice

    def update_options(
        self,
        *,
        voice: NotGivenOr[str] = NOT_GIVEN,
        response_format: NotGivenOr[RESPONSE_FORMATS] = NOT_GIVEN,
    ) -> None:
        if is_given(voice):
            self._opts.voice = voice
        if is_given(response_format):
            self._opts.response_format = response_format

    def synthesize(
        self,
        text: str,
        *,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> ChunkedStream:
        return ChunkedStream(tts=self, input_text=text, conn_options=conn_options)

    def prewarm(self) -> None:
        async def _prewarm() -> None:
            try:
                await self._client.get(f"{self._base_url}/health")
            except Exception:
                pass

        self._prewarm_task = asyncio.create_task(_prewarm())

    async def aclose(self) -> None:
        if self._prewarm_task:
            await aio.cancel_and_wait(self._prewarm_task)
        await self._client.aclose()


class ChunkedStream(tts.ChunkedStream):
    def __init__(
        self, *, tts: IndexTTS, input_text: str, conn_options: APIConnectOptions
    ) -> None:
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._tts: IndexTTS = tts
        self._opts = replace(tts._opts)

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        try:
            # 构建请求数据（兼容 OpenAI 格式）
            request_data = {
                "model": "tts-1",  # 可以是任意值，你的服务会忽略它
                "input": self.input_text,
                "voice": self._opts.voice,
            }

            # 发送请求到本地 TTS 服务
            response = await self._tts._client.post(
                f"{self._tts._base_url}/audio/speech",
                json=request_data,
                timeout=self._tts._timeout,
            )

            response.raise_for_status()

            # 获取音频数据
            audio_data = response.content

            # 初始化输出
            output_emitter.initialize(
                request_id="",
                sample_rate=SAMPLE_RATE,
                num_channels=NUM_CHANNELS,
                mime_type=f"audio/{self._opts.response_format}",
            )

            # 推送音频数据
            output_emitter.push(audio_data)
            output_emitter.flush()

        except httpx.TimeoutException:
            raise APITimeoutError() from None
        except httpx.HTTPStatusError as e:
            raise APIStatusError(
                message=str(e),
                status_code=e.response.status_code,
                request_id="",
                body=e.response.text,
            ) from None
        except Exception as e:
            raise APIConnectionError() from e
