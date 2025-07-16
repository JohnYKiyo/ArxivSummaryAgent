"""Arxiv agent for paper processing."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from arxiv.agents.format_agent import arxiv_format_agent
from arxiv.tools import (
    arxiv_eprint_fetcher_tool,
    arxiv_file_lister_tool,
    arxiv_file_reader_tool,
    arxiv_tex_expander_tool,
)

INSTRUCTION = """
あなたはarXiv論文処理エージェントです。

## 処理フロー
1. **URL検証**: 受け取ったURLがarXiv URLかチェック
   - arXiv URLでない場合: "処理できないURLです" と返答
   - arXiv URLの場合: 次のステップへ

2. **e-printファイルダウンロード**: arXivからe-printファイル一式をダウンロード

3. **メインファイル特定**:
   - arxiv_file_lister_toolを使ってファイル一覧を取得
   - 各ファイルの内容をarxiv_file_reader_toolで確認
   - 取得したファイル情報を分析して、LLMでメインファイルを特定
   - メインファイルが見つからない場合はエラー

4. **TeXファイル展開**:
   - メインファイルが.texの場合、input文を展開して1つのファイルに統合
   - メインファイルがPDFの場合は展開不要

5. **解析対象ファイル情報の伝達**:
   - arxiv_format_agentを使って、解析対象ファイルの情報を整形
   - input_file: 解析対象ファイルパス
   - file_type: "tex" または "pdf"
   - paper_dir: 保存ディレクトリ

## メインファイル特定の基準

### TeXファイルの場合
1. **begin documentの存在**: メインのTeXファイルには通常begin documentが含まれます
2. **ファイル名の特徴**:
   - main.tex, paper.tex, article.tex などの一般的な名前
   - 論文IDと同じ名前（例: 1706.03762.tex）
   - 短く、シンプルな名前
3. **ファイルサイズ**: 他のTeXファイルより大きい場合が多い
4. **内容の特徴**:
   - タイトル、著者、アブストラクトが含まれる
   - セクション構造（\\section, \\subsection）がある
   - 参考文献（\\bibliography）が含まれる場合がある

### PDFファイルの場合
- TeXファイルでメインファイルが見つからない場合やpdfファイルをincludeしている場合
- 通常、論文の完成版PDFがメインファイル

## 重要な注意
- 各ステップでエラーが発生した場合は適切なエラーメッセージを返す
- format_agentの出力（status, input_file, file_type, paper_dir）を必ず保持すること
- この情報は後続のエージェントに渡されるため、失ってはいけない
- メインファイル特定では、複数のファイルを比較して最も適切なものを選択すること

常に日本語で応答してください。
"""

arxiv_agent = Agent(
    name="arxiv_paper_processor",
    model="gemini-2.5-flash",
    description="arXiv論文のダウンロード、LLMによるメインファイル特定、TeX展開、翻訳戦略決定を行うエージェント",
    instruction=INSTRUCTION,
    tools=[
        arxiv_eprint_fetcher_tool,
        arxiv_file_lister_tool,
        arxiv_file_reader_tool,
        arxiv_tex_expander_tool,
        AgentTool(agent=arxiv_format_agent, skip_summarization=True),
    ],
    output_key="arxiv_result",
)
