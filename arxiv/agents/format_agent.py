"""Format agents for standardizing output formats."""

from typing import Literal, Optional

from google.adk.agents import Agent
from pydantic import BaseModel

INSTRUCTION = """
あなたは出力形式を統一するエージェントです。

## 役割
- 入力を受け取り、指定されたJSON形式で出力する
- データの整合性を保つ

常に日本語で応答してください。
"""


class ArxivFormatOutput(BaseModel):
    status: Literal["success", "error"]
    input_file: str
    file_type: Literal["tex", "pdf"]
    paper_dir: Optional[str] = None


class Metadata(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    abstract: Optional[str] = None


class TranslationFormatOutput(BaseModel):
    status: Literal["success", "error"]
    markdown_file: str
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

# translation_agent用のformat_agent
translation_format_agent = Agent(
    name="translation_format_agent",
    model="gemini-2.5-flash",
    description="translation_agent用の出力形式を統一するエージェント",
    instruction=INSTRUCTION,
    output_schema=TranslationFormatOutput,
    output_key="translation_format_result",
)
