"""Root agent for arXiv paper processing and translation workflow."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from src.agents import arxiv_agent, summary_agent, translation_agent

# Instruction
INSTRUCTION = """
あなたはarXiv論文の処理と翻訳を行うエージェントコーディネーターです。
ユーザーのリクエストに応えること。
場合によってクエリを適切なエージェントにルーティングすること。

## あなたが使えるツール/エージェント
- `arxiv_agent`: arXivのURLを引数に取り、論文をダウンロード・分析し、ファイル情報をJSON形式で返します。
- `translation_agent`: `arxiv_agent`が処理した論文の情報を引数に取り、論文全体を翻訳します。

## ワークフローの概要
1. ユーザーからarXivのURLが入力されたら、`arxiv_agent`を呼び出して論文を処理します。
2. 論文処理後、ユーザーが翻訳を希望したら、`translation_agent`を呼び出して翻訳を実行します。
3. 論文処理後、ユーザーが要約を希望したら、`summary_agent`を呼び出して要約を実行します。
"""
# エージェントをツールとしてラップする
arxiv_tool = AgentTool(
    agent=arxiv_agent,
    skip_summarization=False,
)

translation_tool = AgentTool(
    agent=translation_agent,
    skip_summarization=False,
)


# arXiv論文処理・翻訳ワークフロー用Root Agent
root_agent = LlmAgent(
    name="paper_summary_agent",
    model="gemini-2.5-flash",
    description="arXiv論文の処理と翻訳を管理するルートエージェント",
    instruction=INSTRUCTION,
    sub_agents=[arxiv_agent, translation_agent, summary_agent],
    output_key="paper_summary_agent_result",
)
