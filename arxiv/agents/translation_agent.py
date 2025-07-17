"""Translation agent for arXiv papers."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from arxiv.agents.format_agent import translation_format_agent
from arxiv.tools.translation_tools import (
    translation_chunk_merger_tool,
    translation_file_reader_tool,
    translation_markdown_saver_tool,
    translation_metadata_extractor_tool,
    translation_tex_splitter_tool,
)

INSTRUCTION = """
あなたはarXiv論文翻訳エージェントです。

## 役割
- 対象となるデータ（PDF/TeX）の読み込み
- メタデータ（タイトル、著者、要約）を抽出
- 論文を日本語に翻訳
- 翻訳結果をmarkdown形式で保存

入力データ：
{arxiv_format_result}

## 処理手順
1. 入力データを読み込み
2. 必要に応じて翻訳を分割
3. LLMで翻訳実行
4. 翻訳結果をmarkdownで保存（outputディレクトリに保存）
5. メタデータを抽出
6. translation_format_agentを使って結果を整形

## 重要な設定
- 翻訳結果は agent_outputs ディレクトリに保存してください

常に日本語で応答してください。
"""

translation_agent = Agent(
    name="arxiv_translation_agent",
    model="gemini-2.5-flash",
    description="arXiv論文のPDF/TeXファイルを日本語に翻訳し、markdown形式で保存するエージェント",
    instruction=INSTRUCTION,
    tools=[
        translation_file_reader_tool,
        translation_markdown_saver_tool,
        translation_metadata_extractor_tool,
        translation_tex_splitter_tool,
        translation_chunk_merger_tool,
        AgentTool(agent=translation_format_agent, skip_summarization=True),
    ],
    output_key="translation_result",
)
