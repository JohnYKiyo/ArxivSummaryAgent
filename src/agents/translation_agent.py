"""Translation agent for arXiv papers."""

from google.adk.agents import Agent

from src.tools.translation_tools import translate_file_tool

INSTRUCTION = """
あなたはarXiv論文翻訳エージェントです。

## 役割
- 対象となる論文のTeXファイルを読み込み、内容を翻訳してMarkdownファイルとして保存します。


## 処理手順
1. `translation_file_reader_tool` を使って入力ファイルを読み込みます。paper_id とファイル内容（content）を取得してください。
2. `translation_tex_splitter_tool` を使って、ファイル内容をチャンクに分割します。
3. `translation_chunks_processor_tool` を呼び出します。引数として、ステップ2で得られたチャンクのリストと、ステップ1で得られたpaper_idを渡してください。
4. `translation_chunks_processor_tool` から返されたファイルパスが、最終的な成果物です。

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
