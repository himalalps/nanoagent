from typing import Dict, Any
from .base import Tool

class ReadTool(Tool):
    @property
    def name(self) -> str:
        return "read"
    
    @property
    def description(self) -> str:
        return "Read file content"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "File path"
                }
            },
            "required": ["file_path"]
        }
    
    def execute(self, **kwargs) -> str:
        file_path = kwargs.get("file_path")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"Content of {file_path}:\n{content}"
        except Exception as e:
            return f"Error: {str(e)}"