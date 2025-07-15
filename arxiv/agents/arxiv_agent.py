"""Arxiv agent for paper processing."""

from google.adk.agents import Agent

from arxiv.instructions.utils import load_instruction
from arxiv.tools import (
    arxiv_eprint_fetcher_tool,
    arxiv_file_lister_tool,
    arxiv_file_reader_tool,
    arxiv_tex_expander_tool,
)

# arXiv論文処理エージェント
arxiv_agent = Agent(
    name="arxiv_paper_processor",
    model="gemini-2.5-flash",
    description="arXiv論文のダウンロード、LLMによるメインファイル特定、TeX展開、翻訳戦略決定を行うエージェント",
    instruction=load_instruction("arxiv_agent_instruction.txt"),
    tools=[
        arxiv_eprint_fetcher_tool,
        arxiv_file_lister_tool,
        arxiv_file_reader_tool,
        arxiv_tex_expander_tool,
    ],
)
