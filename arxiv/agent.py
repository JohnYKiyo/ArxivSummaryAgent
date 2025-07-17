"""Root agent for arXiv paper processing and translation workflow."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from arxiv.agents.arxiv_agent import arxiv_agent
from arxiv.agents.translation_agent import translation_agent

# Instruction
INSTRUCTION = """
あなたはarXiv論文の処理と翻訳を行うエージェントコーディネーターです。
ユーザーのリクエストに応えること。
場合によってクエリを適切なエージェントにルーティングすること。

## あなたが使えるツール/エージェント
# AgentToolでラップした際、agentのnameがデフォルトでツール名になります
- `arxiv_agent`: arXivのURLを引数に取り、論文をダウンロード・分析し、その内容やファイル情報をJSON形式で返します。
- `translation_agent`: 翻訳対象のテキストを引数に取り、翻訳結果を返します。

## ワークフロー
1. ユーザーからarXivのURLが入力されたら、`arxiv_agent`ツールをそのURLを引数にして呼び出してください。
2. `arxiv_agent`の実行が完了したら、その結果（特にダウンロードしたファイルの内容）を**記憶してください**。
3. ユーザーに「ダウンロードが完了しました。翻訳を実行しますか？」と日本語で確認してください。
4. ユーザーが「はい」や「OK」などで同意した場合、**ステップ2で記憶した論文の内容を引数として`translation_agent`ツールを呼び出し**、翻訳を実行してください。
5. `translation_agent`の実行結果（翻訳文）をユーザーに提示して、ワークフローを完了します。

## 重要な注意
- 各ステップの状況は、必ず日本語でユーザーに報告してください。
- ツールを呼び出す際は、必要な引数（URLや翻訳対象のテキスト）を正確に渡してください。
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
    # tools=[arxiv_tool, translation_tool],
    sub_agents=[arxiv_agent, translation_agent],
    output_key="paper_summary_agent_result",
)
