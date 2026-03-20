import logging

logger = logging.getLogger(__name__)


class TokenManager:
    """Token 管理器，负责 token 使用情况的记录和统计"""

    def __init__(self):
        self.total_prompt_tokens = 0  # 总 prompt token 数
        self.total_completion_tokens = 0  # 总 completion token 数
        self.reasoning_tokens = 0  # 推理 token 数
        self.current_total_tokens = 0  # 当前总 tokens 数

    def record_token_usage(self, response):
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
            return current_total

    def get_token_stats(self):
        """获取 token 统计信息"""
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "current_total_tokens": self.current_total_tokens,
        }

    def reset_current_tokens(self):
        """重置当前 token 计数"""
        self.current_total_tokens = 0
