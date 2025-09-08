"""Translation agent for arXiv papers."""

from google.adk.agents import Agent

from .tools import translate_file_tool

INSTRUCTION = """
あなたはarXiv論文翻訳エージェントです。

## 役割
- 対象となる論文のTeXファイルを読み込み、内容を翻訳してMarkdownファイルとして保存します。

## 処理手順
1. `translate_file_tool` を使って、入力ファイルを翻訳します。
2. `translate_file_tool` から返されたファイルパスが、最終的な成果物です。


常に日本語で応答してください。
"""

translation_agent = Agent(
    name="arxiv_translation_agent",
    model="gemini-2.5-flash",
    description="arXiv論文のPDF/TeXファイルを日本語に翻訳し、markdown形式で保存するエージェント",
    instruction=INSTRUCTION,
    tools=[
        translate_file_tool,
    ],
    output_key="translation_result",
)
