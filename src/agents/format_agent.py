"""Format agents for standardizing output formats."""

from google.adk.agents import Agent

from src.agents.schemas import ArxivFormatOutput

INSTRUCTION = """
あなたは出力形式を統一するエージェントです。

## 役割
- 入力を受け取り、指定されたJSON形式で出力する
- データの整合性を保つ
"""


# arxiv_agent用のformat_agent
arxiv_format_agent = Agent(
    name="arxiv_format_agent",
    model="gemini-2.5-flash",
    description="arxiv_agent用の出力形式を統一するエージェント",
    instruction=INSTRUCTION,
    output_schema=ArxivFormatOutput,
    output_key="arxiv_format_result",
)
