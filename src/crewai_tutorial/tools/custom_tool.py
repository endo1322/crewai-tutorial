from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class MyCustomToolInput(BaseModel):
    """MyCustomTool の入力スキーマ。"""
    argument: str = Field(..., description="引数の説明。")

class MyCustomTool(BaseTool):
    name: str = "ツールの名前"
    description: str = (
        "このツールが何に役立つかの明確な説明。エージェントがツールを使用するためにこの情報が必要です。"
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
