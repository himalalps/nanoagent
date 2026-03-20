import datetime
import logging
import os
from typing import Any, Dict, List, Optional

from openai import OpenAI

from tools import execute_tool, get_tools_schema

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

        # 初始化消息和 token 统计
        self.messages = []  # 历史消息列表
        self.total_prompt_tokens = 0  # 总 prompt token 数
        self.total_completion_tokens = 0  # 总 completion token 数
        self.reasoning_tokens = 0  # 推理 token 数
        self.current_total_tokens = 0  # 当前总 tokens 数

        # 添加系统消息
        self.messages.append(
            {
                "role": "system",
                "content": "You are a helpful assistant that can use tools to complete tasks.",
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

        # 添加用户输入到历史消息
        self.messages.append({"role": "user", "content": user_input})

        # 检查是否需要 compact
        self._check_compact()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools_schema,
            tool_choice="auto",
        )

        # 记录 token 使用情况
        self._record_token_usage(response)

        logger.info(f"Model response received: {response}")
        result = self._process_response(response)
        logger.info(f"Final response: {result}")
        return result

    def get_context_usage(self):
        """获取当前上下文使用情况"""
        if self.max_tokens > 0:
            usage_percentage = (self.current_total_tokens / self.max_tokens) * 100
            return {
                "current_tokens": self.current_total_tokens,
                "threshold": self.max_tokens,
                "percentage": round(usage_percentage, 2),
            }
        return {
            "current_tokens": self.current_total_tokens,
            "threshold": self.max_tokens,
            "percentage": 0,
        }

    def _check_compact(self):
        """检查是否需要压缩对话历史"""
        if self.current_total_tokens > self.compact_threshold:
            compact_message = f"Total tokens ({self.current_total_tokens}) exceed threshold ({self.compact_threshold}), performing compact"
            logger.info(compact_message)
            print(f"\n=== Compact Triggered ===")
            print(compact_message)
            print("=======================\n")
            self._compact_messages()

    def _compact_messages(self):
        """压缩对话历史，保持系统消息并总结之前的对话"""
        # 保留系统消息
        system_message = None
        for msg in self.messages:
            if msg.get("role") == "system":
                system_message = msg
                break

        # 提取除系统消息外的所有消息
        non_system_messages = [
            msg for msg in self.messages if msg.get("role") != "system"
        ]

        # 构建总结请求，将所有非系统消息完整传递
        summary_prompt = ""
        for msg in non_system_messages:
            role = msg.get("role")
            content = msg.get("content", "")
            summary_prompt += f"{role}: {content}\n"

        # 添加用户指定的总结prompt
        summary_prompt += (
            "\n"
            + """You have been working on the task described above but have not yet completed it. Write a continuation summary that will allow you (or another instance of yourself) to resume work efficiently in a future context window where the conversation history will be replaced with this summary. Your summary should be structured, concise, and actionable. Include: 1. **Task Overview**   - The user's core request and success criteria   - Any clarifications or constraints they specified 2. **Current State**   - What has been completed so far   - Files created, modified, or analyzed (with paths if relevant)   - Key outputs or artifacts produced 3. **Important Discoveries**   - Technical constraints or requirements uncovered   - Decisions made and their rationale   - Errors encountered and how they were resolved   - What approaches were tried that didn't work (and why) 4. **Next Steps**   - Specific actions needed to complete the task   - Any blockers or open questions to resolve   - Priority order if multiple steps remain 5. **Context to Preserve**   - User preferences or style requirements   - Domain-specific details that aren't obvious   - Any promises made to the user Be concise but complete—err on the side of including information that would prevent duplicate work or repeated mistakes. Write in a way that enables immediate resumption of the task. Wrap your summary in <summary></summary> tags."""
        )

        # 调用模型进行总结
        summary_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个对话总结助手，负责根据对话历史生成结构化的总结",
                },
                {"role": "user", "content": summary_prompt},
            ],
        )

        # 获取总结结果
        summary = ""
        if hasattr(summary_response, "choices") and len(summary_response.choices) > 0:
            message = summary_response.choices[0].message
            if hasattr(message, "content"):
                summary = message.content

        start_idx = summary.find("<summary>")
        end_idx = summary.find("</summary>")
        if start_idx != -1 and end_idx != -1:
            summary = summary[start_idx : end_idx + len("</summary>")].strip()

        logger.info(f"Compact summary: {summary}")

        # 重建 messages 列表：系统消息 + 总结 + 最新的用户输入
        self.messages = []
        if system_message:
            self.messages.append(system_message)

        # 添加总结作为 user 消息
        self.messages.append({"role": "user", "content": summary})

        # 重置 token 计数
        self.current_total_tokens = 0
        logger.info("Messages compacted successfully")

    def _record_token_usage(self, response):
        """记录 token 使用情况"""
        if hasattr(response, "usage"):
            usage = response.usage
            current_completion_tokens = usage.completion_tokens
            self.total_completion_tokens += current_completion_tokens

            # 更新当前总 tokens 数
            current_prompt_tokens = 0
            if hasattr(usage, "prompt_tokens"):
                current_prompt_tokens = usage.prompt_tokens
                self.total_prompt_tokens += current_prompt_tokens

            # 计算当前总 tokens
            current_total = current_prompt_tokens + current_completion_tokens
            self.current_total_tokens = current_total
            logger.info(f"Current total tokens: {self.current_total_tokens}")

            # 记录推理 token 数
            if hasattr(usage, "reasoning_tokens"):
                current_reasoning_tokens = usage.reasoning_tokens
                self.reasoning_tokens += current_reasoning_tokens
                logger.info(
                    f"Token usage: completion={current_completion_tokens}, reasoning={current_reasoning_tokens}, Total prompt: {self.total_prompt_tokens}, Total completion: {self.total_completion_tokens}, Total reasoning: {self.reasoning_tokens}"
                )
            else:
                logger.info(
                    f"Token usage: completion={current_completion_tokens}, Total prompt: {self.total_prompt_tokens}, Total completion: {self.total_completion_tokens}"
                )

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
            # 输出模型的 content 和 reasoning
            if hasattr(message, "content") and message.content:
                print("\n=== Model Content ===")
                print(f"[Content] {message.content.strip()}")
            if hasattr(message, "reasoning") and message.reasoning:
                print("\n=== Model Reasoning ===")
                print(f"[Reasoning] {message.reasoning.strip()}")
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

        # 在终端显示工具调用信息
        print("\n=== Tool Call ===")
        print(f"[Tool Call] {tool_name} with args: {tool_args}")

        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
        result = execute_tool(tool_name, tool_args)

        # 在终端显示工具执行结果
        print("\n=== Tool Result ===")
        print(f"[Tool Result] {result.strip()}")
        print("=================")

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

        # 检查是否需要 compact
        self._check_compact()

        # 使用完整的历史消息调用 API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools_schema,
            tool_choice="auto",
        )

        # 记录 token 使用情况
        self._record_token_usage(response)

        logger.info(f"Model response received for tool results: {response}")
        return self._process_response(response)


# 加载环境变量的辅助函数
def load_dotenv():
    from dotenv import load_dotenv as _load_dotenv

    _load_dotenv()
