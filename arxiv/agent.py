"""Root agent for arXiv paper processing and translation workflow."""

from google.adk.agents import LlmAgent

from arxiv.agents.arxiv_agent import arxiv_agent

# from arxiv.agents.translation_agent import translation_agent

# Instruction
INSTRUCTION = """
あなたはarXiv論文処理・翻訳・要約を行うエージェントのコーディネーターです。

## 役割
- ユーザー入力に応じて適切なエージェントを呼び出す

## サブエージェント
- arxiv_agent: arXiv論文のダウンロード・分析・arXivのファイル一覧取得・ファイル内容の読み込み
- translation_agent: 論文の翻訳・翻訳をmarkdownへ保存

## ワークフロー
1. arXiv URLが入力された場合：
    1. arxiv_agentを呼び出して論文をダウンロード・分析し、ファイル情報を取得
    2. arxiv_agentの出力（format_agentの結果）を確認：
    3. ダウンロードが成功したら、ユーザーに「ダウンロードが完了しました。スムーズに翻訳を実行しますか？」と確認する
    4. ユーザーがOKした場合、translation_agentを呼び出して翻訳を実行する.
    5. 翻訳結果とメタデータを統合して返す

2. その他の場合：
    1. 状況に応じて適切なエージェントを選択

## 重要な注意
- 各ステップで進行状況やエラーを日本語で丁寧に報告すること

"""

# arXiv論文処理・翻訳ワークフロー用Root Agent
root_agent = arxiv_agent

#
# LlmAgent(
#     name="arxiv_paper_workflow_manager",
#     model="gemini-2.5-flash",
#     description="arXiv論文の処理と翻訳を管理するルートエージェント",
#     instruction=INSTRUCTION,
#     sub_agents=[arxiv_agent],
#     output_key="workflow_result",
# )
