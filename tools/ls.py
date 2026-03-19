import os
from typing import Dict, Any, List
from .base import Tool

class LsTool(Tool):
    @property
    def name(self) -> str:
        return "ls"
    
    @property
    def description(self) -> str:
        return "List directory contents"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path (default: current directory)"
                }
            }
        }
    
    def execute(self, **kwargs) -> str:
        path = kwargs.get("path", ".")
        
        try:
            items = os.listdir(path)
            result = f"Contents of {path}:\n"
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    result += f"  📁 {item}/\n"
                else:
                    result += f"  📄 {item}\n"
            return result
        except Exception as e:
            return f"Error: {str(e)}"