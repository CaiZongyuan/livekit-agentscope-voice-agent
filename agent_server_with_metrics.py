import logging
import asyncio
import os
import json
import uuid
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
import websockets

_ = load_dotenv(override=True)

logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)

from livekit import agents
from livekit.agents import Agent, AgentSession
from livekit.plugins import (
    openai,
    minimax,
    silero,
)

from adapter.qwen_asr_stt import STT as QwenSTT
from livekit.agents.metrics import LLMMetrics, STTMetrics, TTSMetrics, EOUMetrics


class MetricsCollector:
    """指标收集器，负责收集并发送性能指标到监控服务"""

    def __init__(
        self, session_id: str, monitor_server_url: str = "ws://localhost:8001/ws"
    ):
        self.session_id = session_id
        self.monitor_server_url = monitor_server_url
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False

    async def connect(self):
        """连接到监控服务"""
        try:
            self.websocket = await websockets.connect(self.monitor_server_url)
            self.is_connected = True
            logger.info(f"已连接到监控服务: {self.monitor_server_url}")
        except Exception as e:
            logger.error(f"连接监控服务失败: {e}")
            self.is_connected = False

    async def disconnect(self):
        """断开连接"""
        if self.websocket and self.is_connected:
            await self.websocket.close()
            self.is_connected = False
            logger.info("已断开监控服务连接")

    async def send_metric(self, metric_type: str, data: dict):
        """发送指标数据"""
        if not self.is_connected or not self.websocket:
            # 尝试重新连接
            await self.connect()
            if not self.is_connected:
                logger.warning("无法连接到监控服务，跳过指标发送")
                return

        try:
            metric_data = {
                "timestamp": datetime.now().isoformat(),
                "metric_type": metric_type,
                "session_id": self.session_id,
                "data": data,
            }
            await self.websocket.send(json.dumps(metric_data))
        except Exception as e:
            logger.error(f"发送指标数据失败: {e}")
            self.is_connected = False

    async def send_llm_metrics(self, metrics: LLMMetrics):
        """发送LLM指标"""
        data = {
            "prompt_tokens": metrics.prompt_tokens,
            "completion_tokens": metrics.completion_tokens,
            "tokens_per_second": metrics.tokens_per_second,
            "ttft": metrics.ttft,
        }
        await self.send_metric("llm", data)

    async def send_stt_metrics(self, metrics: STTMetrics):
        """发送STT指标"""
        data = {
            "duration": metrics.duration,
            "audio_duration": metrics.audio_duration,
            "streamed": metrics.streamed,
            "real_time_factor": (
                metrics.duration / metrics.audio_duration
                if metrics.audio_duration > 0
                else 0
            ),
        }
        await self.send_metric("stt", data)

    async def send_eou_metrics(self, metrics: EOUMetrics):
        """发送EOU指标"""
        data = {
            "end_of_utterance_delay": metrics.end_of_utterance_delay,
            "transcription_delay": metrics.transcription_delay,
        }
        await self.send_metric("eou", data)

    async def send_tts_metrics(self, metrics: TTSMetrics):
        """发送TTS指标"""
        data = {
            "ttfb": metrics.ttfb,
            "duration": metrics.duration,
            "audio_duration": metrics.audio_duration,
            "streamed": metrics.streamed,
            "real_time_factor": (
                metrics.duration / metrics.audio_duration
                if metrics.audio_duration > 0
                else 0
            ),
        }
        await self.send_metric("tts", data)


class MetricsAssistant(Agent):
    """带指标收集的助手类"""

    def __init__(self, session_id: str) -> None:
        super().__init__(
            instructions="""你是一位有帮助的语音 AI 助手，名字叫王凯。
            你会热情地解答用户的问题，并从你广博的知识中提供信息。
            你的回答应简洁明了、直奔主题，且不使用任何复杂的格式或标点（包括表情符号、星号或其他符号）。
            你充满好奇、友善，并且富有幽默感。""",
        )
        self.session_id = session_id
        self.metrics_collector = MetricsCollector(session_id)

    async def start_session(self):
        """启动会话并连接监控服务"""
        await self.metrics_collector.connect()
        logger.info(f"启动带监控的助手会话: {self.session_id}")

    async def end_session(self):
        """结束会话并断开监控连接"""
        await self.metrics_collector.disconnect()
        logger.info(f"结束助手会话: {self.session_id}")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""你是一位有帮助的语音 AI 助手，名字叫王凯。
            你会热情地解答用户的问题，并从你广博的知识中提供信息。
            你的回答应简洁明了、直奔主题，且不使用任何复杂的格式或标点（包括表情符号、星号或其他符号）。
            你充满好奇、友善，并且富有幽默感。""",
        )


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()  # 首先连接到房间

    # 生成唯一的会话ID
    session_id = str(uuid.uuid4())
    logger.info(f"开始新的语音会话: {session_id}")

    # 创建带监控的助手实例
    agent = MetricsAssistant(session_id)
    await agent.start_session()

    # 获取各个组件的引用用于指标收集
    stt = QwenSTT(
        model="qwen3-asr-flash",
        language="zh",
        enable_itn=True,  # 启用逆文本规范化
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
    )

    llm = openai.LLM.with_deepseek(model="deepseek-chat")
    tts = minimax.TTS(
        base_url="https://api.minimaxi.com",
        model="speech-2.6-hd",
        voice="Chinese (Mandarin)_Gentleman",
    )

    # 设置指标收集回调
    def llm_metrics_wrapper(metrics: LLMMetrics):
        asyncio.create_task(agent.metrics_collector.send_llm_metrics(metrics))
        # 同时打印到控制台用于调试
        print(f"\n--- 大模型(LLM)指标 [{session_id[:8]}...] ---")
        print(f"提示词Tokens数量: {metrics.prompt_tokens}")
        print(f"补全Tokens数量: {metrics.completion_tokens}")
        print(f"每秒Tokens数量: {metrics.tokens_per_second:.4f}")
        print(f"第一个Token延迟: {metrics.ttft:.4f}秒")
        print("-----------------------\n")

    def stt_metrics_wrapper(metrics: STTMetrics):
        asyncio.create_task(agent.metrics_collector.send_stt_metrics(metrics))
        print(f"\n--- 语音转文本(STT)指标 [{session_id[:8]}...] ---")
        print(f"推理耗时: {metrics.duration:.4f}秒")
        print(f"音频时长: {metrics.audio_duration:.4f}秒")
        print(
            f"实时因子: {metrics.duration / metrics.audio_duration if metrics.audio_duration > 0 else 0:.4f}"
        )
        print(f"是否流式处理: {'是' if metrics.streamed else '否'}")
        print("--------------------------\n")

    def eou_metrics_wrapper(metrics: EOUMetrics):
        asyncio.create_task(agent.metrics_collector.send_eou_metrics(metrics))
        print(f"\n--- 语句结束(EOU)指标 [{session_id[:8]}...] ---")
        print(f"语句结束延迟: {metrics.end_of_utterance_delay:.4f}秒")
        print(f"转录延迟: {metrics.transcription_delay:.4f}秒")
        print("---------------------------\n")

    def tts_metrics_wrapper(metrics: TTSMetrics):
        asyncio.create_task(agent.metrics_collector.send_tts_metrics(metrics))
        print(f"\n--- 文本转语音(TTS)指标 [{session_id[:8]}...] ---")
        print(f"首包延迟: {metrics.ttfb:.4f}秒")
        print(f"推理耗时: {metrics.duration:.4f}秒")
        print(f"音频时长: {metrics.audio_duration:.4f}秒")
        print(
            f"实时因子: {metrics.duration / metrics.audio_duration if metrics.audio_duration > 0 else 0:.4f}"
        )
        print(f"是否流式处理: {'是' if metrics.streamed else '否'}")
        print("--------------------------\n")

    # 注册指标回调
    llm.on("metrics_collected", llm_metrics_wrapper)
    stt.on("metrics_collected", stt_metrics_wrapper)
    stt.on("eou_metrics_collected", eou_metrics_wrapper)
    tts.on("metrics_collected", tts_metrics_wrapper)

    # 创建会话
    session = AgentSession(
        stt=stt,
        llm=llm,
        tts=tts,
        vad=silero.VAD.load(),
    )

    try:
        await session.start(
            room=ctx.room,
            agent=agent,
        )

        await session.generate_reply(
            instructions="向用户打招呼，简短介绍自己，然后询问用户的问题。"
        )

        # 保持会话运行
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"会话运行出错: {e}")
    finally:
        # 清理资源
        await agent.end_session()
        logger.info(f"语音会话结束: {session_id}")


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
