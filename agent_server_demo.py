import logging
import asyncio
import os
from dotenv import load_dotenv

_ = load_dotenv(override=True)

logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)

from livekit import agents
from livekit.agents import Agent, AgentSession
from livekit.plugins import openai, silero, minimax

from providers.qwen_asr_stt import STT as QwenSTT
from providers.local_indexTTS import IndexTTS
from providers.local_indextts_chaos import TTS as LocalTTS
from providers.kokoro_tts import TTS as KokoroTTS


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""你是一位有帮助的语音 AI 助手，名字叫娜娜。
            你会热情地解答用户的问题，并从你广博的知识中提供信息。
            你的回答应简洁明了、直奔主题。
            你充满好奇、友善，并且富有幽默感。
            注意回答中不要包含表情以及markdown符号""",
        )


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()  # 首先连接到房间

    logger.info("开始新的语音会话")

    # 创建助手实例
    agent = Assistant()

    stt = QwenSTT(
        model="qwen3-asr-flash",
        language="zh",
        enable_itn=True,  # 启用逆文本规范化
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
    )

    llm = openai.LLM.with_deepseek(model="deepseek-chat")
    # tts = minimax.TTS(
    #     base_url="https://api.minimaxi.com",
    #     model="speech-2.6-hd",
    #     voice="Chinese (Mandarin)_Gentleman",
    # )

    # 使用本地 TTS 服务
    # tts = IndexTTS(
    #     base_url="http://localhost:6006",  # 你的本地 TTS 服务地址
    #     voice="jay_klee",  # 替换为你的 speaker.json 中的角色名
    #     response_format="wav",
    #     timeout=30.0,
    # )

    tts = KokoroTTS()

    # tts = LocalTTS(
    #     speaker="忧伤女声.pt",  # 选择你的说话人模型
    #     volume=1.9,
    #     base_url="http://198.18.0.1:9880",  # 本地 TTS 服务地址
    # )

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
        logger.info("语音会话结束")


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
