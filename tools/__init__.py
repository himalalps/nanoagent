from typing import Any, Dict, List

from .bash import BashTool
from .edit import EditTool
from .ls import LsTool
from .read import ReadTool

# 注册所有工具
tools = [EditTool(), LsTool(), BashTool(), ReadTool()]

# 工具字典，用于通过名称查找工具
tool_dict = {tool.name: tool for tool in tools}


def get_tools_schema() -> List[Dict[str, Any]]:
    """返回 OpenAI tools 格式的工具 schema"""
    schema = []
    for tool in tools:
        schema.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
        )
    return schema


def execute_tool(name: str, args: Dict[str, Any]) -> Any:
    """执行指定工具"""
    if name not in tool_dict:
        return f"Error: Tool {name} not found"
    return tool_dict[name].execute(**args)
