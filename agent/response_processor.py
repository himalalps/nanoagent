import json
import logging
from typing import Any, Dict, List

from prompts import SystemPrompt
from tools import execute_tool

logger = logging.getLogger(__name__)


class ResponseProcessor:
    """响应处理器，负责处理模型响应和工具调用"""

    def __init__(self, context_manager, token_manager, tools_schema):
        self.context_manager = context_manager
        self.token_manager = token_manager
        self.tools_schema = tools_schema

    def process_response(self, response, client=None, model=None) -> str:
        """处理模型响应"""
        # 检查是否有工具调用
        tool_calls = []
        if hasattr(response, "choices") and len(response.choices) > 0:
            message = response.choices[0].message
            # 将模型响应添加到历史消息
            self.context_manager.messages.append(
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
                result = self.handle_tool_call(tool_call)
                results.append({"tool_call_id": tool_call.id, "result": result})
            # 将工具结果反馈给模型继续处理
            logger.info("Continuing with tool results")
            if client and model:
                return self.continue_with_tool_results(client, model, results)
            else:
                return results
        else:
            # 直接返回文本结果
            logger.info("No tool calls, returning text response")
            if hasattr(response, "choices") and len(response.choices) > 0:
                message = response.choices[0].message
                if hasattr(message, "content"):
                    return message.content
            return "No response content"

    def handle_tool_call(self, tool_call) -> Any:
        """处理工具调用"""
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

    def continue_with_tool_results(
        self, client, model, tool_results: List[Dict[str, Any]]
    ) -> str:
        """将工具结果反馈给模型继续处理"""
        logger.info(f"Feeding tool results back to model: {tool_results}")

        # 添加工具结果到历史消息（使用 tool 类型）
        for result in tool_results:
            self.context_manager.messages.append(
                {
                    "role": "tool",
                    "content": result["result"],
                    "tool_call_id": result["tool_call_id"],
                }
            )

        # 检查是否需要 compact
        if self.context_manager.check_compact():
            self.context_manager.compact_messages(client, model)

        # 使用完整的历史消息调用 API
        response = client.chat.completions.create(
            model=model,
            messages=self.context_manager.messages,
            tools=self.tools_schema,
            tool_choice="auto",
        )

        # 记录 token 使用情况
        current_total = self.token_manager.record_token_usage(response)
        # 更新 context_manager 中的 current_total_tokens
        self.context_manager.current_total_tokens = current_total

        logger.info(f"Model response received for tool results: {response}")
        return self.process_response(response, client, model)
