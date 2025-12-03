from __future__ import annotations

import asyncio
import io
import wave
from array import array
from dataclasses import dataclass, replace
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

DEFAULT_SPEAKER = "assets/woman-01-zh.wav"
DEFAULT_SPEAKER_EN = "am_adam_男.pt"
DEFAULT_SPEAKER_ZH = "zm_029.pt"
DEFAULT_SPEED = 1.0


@dataclass
class _TTSOptions:
    speaker: str
    speed: float
    speaker_en: str
    speaker_zh: str
    base_url: str


class TTS(tts.TTS):
    def __init__(
        self,
        *,
        speaker: str = DEFAULT_SPEAKER,
        speed: float = DEFAULT_SPEED,
        speaker_en: str = DEFAULT_SPEAKER_EN,
        speaker_zh: str = DEFAULT_SPEAKER_ZH,
        # base_url: str = "http://localhost:9880",
        base_url: str = "http://192.168.2.30:9880",
    ) -> None:
        """
        Kokoro TTS provider.

        Args:
            speaker: Reference audio, e.g. "参考音音频/trump.wav"
            speed: Playback speed, default 1.0
            speaker_en: English voice model
            speaker_zh: Chinese voice model
            base_url: Service base URL
        """
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),
            sample_rate=SAMPLE_RATE,
            num_channels=NUM_CHANNELS,
        )

        self._opts = _TTSOptions(
            speaker=speaker,
            speed=speed,
            speaker_en=speaker_en,
            speaker_zh=speaker_zh,
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
        return "kokoro-tts"

    def update_options(
        self,
        *,
        speaker: NotGivenOr[str] = NOT_GIVEN,
        speed: NotGivenOr[float] = NOT_GIVEN,
        speaker_en: NotGivenOr[str] = NOT_GIVEN,
        speaker_zh: NotGivenOr[str] = NOT_GIVEN,
    ) -> None:
        if is_given(speaker):
            self._opts.speaker = speaker
        if is_given(speed):
            self._opts.speed = speed
        if is_given(speaker_en):
            self._opts.speaker_en = speaker_en
        if is_given(speaker_zh):
            self._opts.speaker_zh = speaker_zh

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
                params = {
                    "text": "test",
                    "speaker": self._opts.speaker,
                    "speed": self._opts.speed,
                    "speaker_en": self._opts.speaker_en,
                    "speaker_zh": self._opts.speaker_zh,
                }
                url = f"{self._opts.base_url}/?{urlencode(params)}"
                await self._client.get(url)
            except Exception:
                pass

        self._prewarm_task = asyncio.create_task(_prewarm())

    async def aclose(self) -> None:
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

    def _normalize_wav(
        self, wav_bytes: bytes
    ) -> tuple[bytes, int, int]:
        """
        Kokoro 服务返回的 WAV 是 float32 (format=3)，LiveKit 目前只接受 PCM16。
        这里把 float32 WAV 转成 PCM16 WAV，其它格式原样返回。
        """
        sample_rate = SAMPLE_RATE
        num_channels = NUM_CHANNELS

        try:
            if len(wav_bytes) < 12:
                return wav_bytes, sample_rate, num_channels

            if wav_bytes[:4] != b"RIFF" or wav_bytes[8:12] != b"WAVE":
                return wav_bytes, sample_rate, num_channels

            pos = 12
            audio_format = None
            bits_per_sample = None
            data_offset = None
            data_size = None

            while pos + 8 <= len(wav_bytes):
                chunk_id = wav_bytes[pos : pos + 4]
                chunk_size = int.from_bytes(
                    wav_bytes[pos + 4 : pos + 8], byteorder="little"
                )
                pos += 8

                if chunk_id == b"fmt " and pos + 16 <= len(wav_bytes):
                    audio_format = int.from_bytes(
                        wav_bytes[pos : pos + 2], byteorder="little"
                    )
                    num_channels = int.from_bytes(
                        wav_bytes[pos + 2 : pos + 4], byteorder="little"
                    )
                    sample_rate = int.from_bytes(
                        wav_bytes[pos + 4 : pos + 8], byteorder="little"
                    )
                    bits_per_sample = int.from_bytes(
                        wav_bytes[pos + 14 : pos + 16], byteorder="little"
                    )
                elif chunk_id == b"data":
                    data_offset = pos
                    data_size = chunk_size
                    break

                # chunk 数据按偶数字节对齐
                pos += chunk_size + (chunk_size & 1)

            if (
                audio_format != 3
                or bits_per_sample != 32
                or data_offset is None
                or data_size is None
            ):
                return wav_bytes, sample_rate, num_channels

            float_data = array("f")
            float_data.frombytes(wav_bytes[data_offset : data_offset + data_size])

            pcm16 = array("h")
            for sample in float_data:
                clamped = max(-1.0, min(1.0, sample))
                pcm16.append(int(clamped * 32767))

            buf = io.BytesIO()
            with wave.open(buf, "wb") as wf:
                wf.setnchannels(num_channels)
                wf.setsampwidth(2)  # PCM16
                wf.setframerate(sample_rate)
                wf.writeframes(pcm16.tobytes())

            return buf.getvalue(), sample_rate, num_channels

        except Exception:
            # 回退：保留原始数据，至少不会阻塞
            return wav_bytes, sample_rate, num_channels

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        try:
            params = {
                "text": self.input_text,
                "speaker": self._opts.speaker,
                "speed": self._opts.speed,
                "speaker_en": self._opts.speaker_en,
                "speaker_zh": self._opts.speaker_zh,
            }
            url = f"{self._opts.base_url}/?{urlencode(params)}"

            async with self._tts._client.stream(
                "GET",
                url,
                timeout=httpx.Timeout(30, connect=self._conn_options.timeout),
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise APIStatusError(
                        message=f"TTS request failed: {error_text.decode('utf-8', errors='ignore')}",
                        status_code=response.status_code,
                        request_id="",
                        body=error_text,
                    )

                audio_bytes, sample_rate, num_channels = self._normalize_wav(
                    await response.aread()
                )

                request_id = response.headers.get("x-request-id", "")
                output_emitter.initialize(
                    request_id=request_id,
                    sample_rate=sample_rate,
                    num_channels=num_channels,
                    mime_type="audio/wav",
                )

                output_emitter.push(audio_bytes)

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
