from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from src.tools.summary_agent_tools import read_file_tool, save_markdown_tool

REVIEW_INSTRUCTION = """
あなたはレビュー/サーベイ論文の要約を作成するエージェントです。
下記のフォーマットに従って要約を作成してください。

フォーマット:
# [論文のタイトルをここに記入 - タイトルは原文のまま出力]

URL: [論文 URL をここに記入]

発表年: [発表された年をここに記入]

著者:

[著者の名前をここに記入]

著者の所属機関:

[著者の所属する組織や機関をここに記入]

## 要約

[論文の目的、主要な内容、結果、および結論を簡潔にまとめてここに記入]

## レビュー/サーベイ項目

[論文で提案されたレビュー内容/サーベイ内容を箇条書きでここに記入]

## 比較

[それぞれのレビュー内容/サーベイ内容を簡潔にまとめ、論文内で使われている比較表などわかりやすく説明]

## 議論

[論文の結果や結論に関する議論、今後の研究課題、さらなる研究の可能性などをここに記述]
"""

review_summary_agent = Agent(
    name="review_summary_agent",
    model="gemini-2.5-flash",
    description="レビュー/サーベイ論文の要約を作成するエージェントです。",
    instruction=REVIEW_INSTRUCTION,
)

NORMAL_INSTRUCTION = """
あなたは論文の要約を作成するエージェントです。
下記のフォーマットに従って要約を作成してください。

フォーマット:
# [論文のタイトルをここに記入 - タイトルは原文のまま出力]

URL: [論文 URL をここに記入]

発表年: [発表された年をここに記入]

著者:

[著者の名前をここに記入]

著者の所属機関:

[著者の所属する組織や機関をここに記入]

## 要約

[論文の主要な内容、結果、および結論を簡潔にまとめてここに記入]

## 使用された手法

[論文で使用された新しい手法や技術をここに簡潔に記入]

## 技術の主要なポイント

[論文で提案された技術の主要なポイントや特徴を箇条書きでここに記入]

## 先行研究との比較

[この論文の技術やアプローチが先行研究と比較してどのような利点や新規性を持っているかをここに記述]

## 実験方法

[論文で行われた実験や研究の方法をここに記述]

## 議論

[論文の結果や結論に関する議論、今後の研究課題、さらなる研究の可能性などをここに記述]
"""

normal_summary_agent = Agent(
    name="normal_summary_agent",
    model="gemini-2.5-flash",
    description="論文の要約を作成するエージェントです。",
    instruction=NORMAL_INSTRUCTION,
)

INSTRUCTION = """
あなたは論文の要約を作成するエージェントです。
クエリを適切なサブエージェントにルーティングすること。

初めにようやく対象のファイルを read_file_tool で読んでください。
与えられたファイルがレビュー/サーベイ論文ならreview_summary_agentを使ってください。
それ以外ならnormal_summary_agentを使ってください。
最後に、markdown形式で保存するsave_markdown_toolを使ってください。
"""

summary_agent = Agent(
    name="summary_agent",
    model="gemini-2.5-flash",
    description="論文の要約を作成するエージェント",
    instruction=INSTRUCTION,
    tools=[
        AgentTool(
            agent=review_summary_agent,
            skip_summarization=False,
        ),
        AgentTool(
            agent=normal_summary_agent,
            skip_summarization=False,
        ),
        read_file_tool,
        save_markdown_tool,
    ],
    output_key="summary_result",
)
