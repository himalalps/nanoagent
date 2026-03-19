from typing import Dict, Any
from .base import Tool

class EditTool(Tool):
    @property
    def name(self) -> str:
        return "edit"
    
    @property
    def description(self) -> str:
        return "Edit file content"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "File path"
                },
                "old_content": {
                    "type": "string",
                    "description": "Content to replace"
                },
                "new_content": {
                    "type": "string",
                    "description": "New content"
                }
            },
            "required": ["file_path", "old_content", "new_content"]
        }
    
    def execute(self, **kwargs) -> str:
        file_path = kwargs.get("file_path")
        old_content = kwargs.get("old_content")
        new_content = kwargs.get("new_content")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_content not in content:
                return f"Error: Old content not found in file"
            
            new_content = content.replace(old_content, new_content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return f"Successfully edited {file_path}"
        except Exception as e:
            return f"Error: {str(e)}"