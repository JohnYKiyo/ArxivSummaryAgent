"""Root agent for arXiv paper processing and translation workflow."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from src.features.arxiv.agent import arxiv_agent
from src.features.arxiv.tools import arxiv_file_lister_tool
from src.features.arxiv.tools import arxiv_file_reader_tool
from src.features.summary.agent import summary_agent
from src.features.translation.agent import translation_agent

# Instruction
INSTRUCTION = """
あなたはarXiv論文の処理と翻訳を行うエージェントコーディネーターです。
ユーザーのリクエストに応えること。
場合によってクエリを適切なエージェントにルーティングすること。

## あなたが使えるツール/エージェント
- `arxiv_agent`: arXivのURLを引数に取り、論文をダウンロード・分析し、ファイル情報をJSON形式で返します。
- `translation_agent`: `arxiv_agent`が処理した論文の情報を引数に取り、論文全体を翻訳します。
- `summary_agent`: `arxiv_agent`が処理した論文の情報を引数に取り、論文全体を要約します。
- `arxiv_file_lister_tool`: 論文ディレクトリ内のすべてのファイルを取得します。
- `arxiv_file_reader_tool`: 論文ディレクトリ内のファイルを読み込みます。

## ワークフローの概要
- ユーザーからarXivのURLが入力されたら、`arxiv_agent`を呼び出して論文を処理します。
- 論文処理後、ユーザーが翻訳を希望したら、`translation_agent`を呼び出して翻訳を実行します。
ディレクトリを指定した場合は、`arxiv_agent`を呼び出して、メインファイルを特定してください。
- ユーザーが要約を希望したら、`summary_agent`を呼び出して要約を実行します。
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
    name="arxiv_paper_agent",
    model="gemini-2.5-flash",
    description="arXiv論文の処理と翻訳を管理するルートエージェント",
    instruction=INSTRUCTION,
    sub_agents=[arxiv_agent, translation_agent, summary_agent],
    tools=[arxiv_file_lister_tool, arxiv_file_reader_tool],
    output_key="paper_summary_agent_result",
)
