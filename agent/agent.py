import datetime
import logging
import os

from openai import OpenAI

from agent.context_management import ContextManager
from agent.response_processor import ResponseProcessor
from agent.token_management import TokenManager
from agent.utils import load_dotenv
from prompts import SystemPrompt
from tools import get_tools_schema

# 生成日志文件名
os.makedirs("logs", exist_ok=True)
log_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"logs/nanoagent_{log_time}.log"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file)],
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to file: {log_file}")


class CodeAgent:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            base_url=os.getenv("base_url"), api_key=os.getenv("api_key")
        )
        # 从环境变量中读取配置
        self.model = os.getenv("model", "gpt-5-mini")

        # Compact strategy 设置
        self.max_tokens = int(os.getenv("max_tokens", "8000"))  # 最大 token 限制
        compact_ratio = float(os.getenv("compact_ratio", "0.75"))  # 触发 compact 的比例
        self.compact_threshold = int(
            self.max_tokens * compact_ratio
        )  # 计算触发 compact 的阈值

        # 初始化工具
        self.tools_schema = get_tools_schema()

        # 初始化管理器
        self.context_manager = ContextManager(self.max_tokens, self.compact_threshold)
        self.token_manager = TokenManager()
        self.response_processor = ResponseProcessor(
            self.context_manager, self.token_manager, self.tools_schema
        )

        # 添加系统消息
        system_prompt = SystemPrompt()
        self.context_manager.messages.append(
            {
                "role": "system",
                "content": system_prompt.system_render(),
            }
        )
        logger.info(
            f"CodeAgent initialized with config:\n"
            f"  model: {self.model}\n"
            f"  max_tokens: {self.max_tokens}\n"
            f"  compact_ratio: {compact_ratio}\n"
            f"  compact_threshold: {self.compact_threshold}"
        )

    def run(self, user_input: str) -> str:
        """处理用户输入并返回响应"""
        logger.info(f"User input: {user_input}")

        # 更新最新的用户输入
        self.context_manager.update_latest_user_input(user_input)
        # 添加用户输入到历史消息
        self.context_manager.messages.append({"role": "user", "content": user_input})

        # 检查是否需要 compact
        if self.context_manager.check_compact():
            summary_response = self.context_manager.compact_messages(
                self.client, self.model
            )
            # 记录总结过程的 token 使用情况
            self.token_manager.record_token_usage(summary_response)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.context_manager.messages,
            tools=self.tools_schema,
            tool_choice="auto",
        )

        # 记录 token 使用情况
        current_total = self.token_manager.record_token_usage(response)
        # 更新 context_manager 中的 current_total_tokens
        self.context_manager.current_total_tokens = current_total

        logger.info(f"Model response received: {response}")
        result = self.response_processor.process_response(
            response, self.client, self.model
        )

        # 如果 result 为空，重新调用 create
        if not result:
            logger.warning("Empty response received, retrying...")
            result = self._retry_create()

        logger.info(f"Final response: {result}")
        return result

    def _retry_create(self) -> str:
        """重新调用 create 方法获取响应"""
        max_retries = 2  # 最多重试2次

        for attempt in range(max_retries):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.context_manager.messages,
                tools=self.tools_schema,
                tool_choice="auto",
            )

            # 记录 token 使用情况
            current_total = self.token_manager.record_token_usage(response)
            # 更新 context_manager 中的 current_total_tokens
            self.context_manager.current_total_tokens = current_total

            logger.info(f"Retry {attempt + 1} model response received: {response}")
            result = self.response_processor.process_response(
                response, self.client, self.model
            )

            if result:
                return result

            logger.warning(
                f"Retry {attempt + 1} still returned empty response, trying again..."
            )

        return ""

    def get_context_usage(self):
        """获取当前上下文使用情况"""
        return self.context_manager.get_context_usage()
