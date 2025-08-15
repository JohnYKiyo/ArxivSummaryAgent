"""Format agents for standardizing output formats."""

from typing import Literal, Optional

from google.adk.agents import Agent
from pydantic import BaseModel

INSTRUCTION = """
あなたは出力形式を統一するエージェントです。

## 役割
- 入力を受け取り、指定されたJSON形式で出力する
- データの整合性を保つ
"""


class Metadata(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    published_year: Optional[str] = None
    url: Optional[str] = None


class ArxivFormatOutput(BaseModel):
    status: Literal["success", "error"]
    input_file: str
    file_type: Literal["tex", "pdf"]
    paper_dir: Optional[str] = None
    metadata: Optional[Metadata] = None


# arxiv_agent用のformat_agent
arxiv_format_agent = Agent(
    name="arxiv_format_agent",
    model="gemini-2.5-flash",
    description="arxiv_agent用の出力形式を統一するエージェント",
    instruction=INSTRUCTION,
    output_schema=ArxivFormatOutput,
    output_key="arxiv_format_result",
)
