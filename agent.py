import datetime
import logging
import os
from typing import Any, Dict, List, Optional

from openai import OpenAI

from tools import execute_tool, get_tools_schema

# 生成日志文件名
log_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"logs/agent_{log_time}.log"

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
        self.model = os.getenv("model")
        self.previous_response_id = None
        self.tools_schema = get_tools_schema()
        self.messages = []  # 历史消息列表
        self.total_tokens = 0  # 总 token 数
        self.reasoning_tokens = 0  # 推理 token 数
        # 添加系统消息
        self.messages.append(
            {
                "role": "system",
                "content": "You are a helpful assistant that can use tools to complete tasks.",
            }
        )
        logger.info("CodeAgent initialized")

    def run(self, user_input: str) -> str:
        """处理用户输入并返回响应"""
        logger.info(f"User input: {user_input}")

        # 添加用户输入到历史消息
        self.messages.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools_schema,
            tool_choice="auto",
        )

        # 记录 token 使用情况
        if hasattr(response, "usage"):
            usage = response.usage
            current_completion_tokens = usage.completion_tokens
            self.total_tokens += current_completion_tokens

            # 记录推理 token 数
            if hasattr(usage, "reasoning_tokens"):
                current_reasoning_tokens = usage.reasoning_tokens
                self.reasoning_tokens += current_reasoning_tokens
                logger.info(
                    f"Token usage: completion={current_completion_tokens}, reasoning={current_reasoning_tokens}, Total tokens: {self.total_tokens}, Total reasoning: {self.reasoning_tokens}"
                )
            else:
                logger.info(
                    f"Token usage: completion={current_completion_tokens}, Total tokens: {self.total_tokens}"
                )

        logger.info(f"Model response received: {response}")
        result = self._process_response(response)
        logger.info(f"Final response: {result}")
        return result

    def _process_response(self, response) -> str:
        """处理模型响应"""
        # 检查是否有工具调用
        tool_calls = []
        if hasattr(response, "choices") and len(response.choices) > 0:
            message = response.choices[0].message
            # 将模型响应添加到历史消息
            self.messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": (
                        message.tool_calls if hasattr(message, "tool_calls") else None
                    ),
                }
            )
            if hasattr(message, "tool_calls") and message.tool_calls:
                tool_calls = message.tool_calls

        if tool_calls:
            logger.info(f"Tool calls detected: {len(tool_calls)}")
            results = []
            for tool_call in tool_calls:
                result = self._handle_tool_call(tool_call)
                results.append({"tool_call_id": tool_call.id, "result": result})
            # 将工具结果反馈给模型继续处理
            logger.info("Continuing with tool results")
            return self._continue_with_tool_results(results)
        else:
            # 直接返回文本结果
            logger.info("No tool calls, returning text response")
            if hasattr(response, "choices") and len(response.choices) > 0:
                message = response.choices[0].message
                if hasattr(message, "content"):
                    return message.content
            return "No response content"

    def _handle_tool_call(self, tool_call) -> Any:
        """处理工具调用"""
        import json

        # 检查工具调用对象的结构（chat completion API 格式）
        if hasattr(tool_call, "function"):
            # chat completion 格式：tool_call.function.name
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments
        else:
            # 其他格式
            tool_name = tool_call.name
            tool_args = tool_call.arguments

        # 确保 tool_args 是一个字典
        if isinstance(tool_args, str):
            try:
                tool_args = json.loads(tool_args)
                logger.info(f"Parsed tool args from JSON: {tool_args}")
            except json.JSONDecodeError:
                logger.error(f"Failed to parse tool args: {tool_args}")
                return f"Error: Failed to parse tool arguments"

        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
        result = execute_tool(tool_name, tool_args)
        logger.info(f"Tool execution result: {result}")
        return result

    def _continue_with_tool_results(self, tool_results: List[Dict[str, Any]]) -> str:
        """将工具结果反馈给模型继续处理"""
        logger.info(f"Feeding tool results back to model: {tool_results}")

        # 添加工具结果到历史消息（使用 tool 类型）
        for result in tool_results:
            self.messages.append(
                {
                    "role": "tool",
                    "content": result["result"],
                    "tool_call_id": result["tool_call_id"],
                }
            )

        # 使用完整的历史消息调用 API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools_schema,
            tool_choice="auto",
        )

        # 记录 token 使用情况
        if hasattr(response, "usage"):
            usage = response.usage
            current_completion_tokens = usage.completion_tokens
            self.total_tokens += current_completion_tokens

            # 记录推理 token 数
            if hasattr(usage, "reasoning_tokens"):
                current_reasoning_tokens = usage.reasoning_tokens
                self.reasoning_tokens += current_reasoning_tokens
                logger.info(
                    f"Token usage: completion={current_completion_tokens}, reasoning={current_reasoning_tokens}, Total tokens: {self.total_tokens}, Total reasoning: {self.reasoning_tokens}"
                )
            else:
                logger.info(
                    f"Token usage: completion={current_completion_tokens}, Total tokens: {self.total_tokens}"
                )

        logger.info(f"Model response received for tool results: {response}")
        return self._process_response(response)


# 加载环境变量的辅助函数
def load_dotenv():
    from dotenv import load_dotenv as _load_dotenv

    _load_dotenv()
