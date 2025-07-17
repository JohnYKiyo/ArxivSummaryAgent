"""Translation tools for arXiv papers."""

import json
import os
import re
from typing import Dict, List


def read_file_for_translation(file_path: str) -> Dict:
    """
    翻訳用にファイルを読み込む

    Args:
        file_path: ファイルのパス（PDFまたはTeX）

    Returns:
        Dict: {
            'success': bool,
            'content': str (成功時),
            'file_type': str (成功時),
            'file_size': int (成功時),
            'error': str (エラー時)
        }
    """
    try:
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}

        file_size = os.path.getsize(file_path)
        file_type = "unknown"

        if file_path.endswith(".tex"):
            # TeXファイルを読み込み
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            file_type = "tex"

        elif file_path.endswith(".pdf"):
            # PDFファイルの場合は、サイズ情報のみ提供
            # 実際のPDF処理は別途実装が必要
            content = f"[PDF file - {file_size} bytes - PDF processing required]"
            file_type = "pdf"

        else:
            # その他のファイルはテキストとして試行
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                file_type = "text"
            except UnicodeDecodeError:
                content = f"[Binary file - {file_size} bytes]"
                file_type = "binary"

        return {
            "success": True,
            "content": content,
            "file_type": file_type,
            "file_size": file_size,
            "file_path": file_path,
        }

    except Exception as e:
        return {"success": False, "error": f"Error reading file: {str(e)}"}


def save_translation_to_markdown(
    translated_content: str, paper_id: str, output_dir: str = "agent_outputs"
) -> Dict:
    """
    翻訳結果をmarkdownファイルとして保存

    Args:
        translated_content: 翻訳されたコンテンツ
        output_dir: 出力ディレクトリ
        paper_id: 論文ID

    Returns:
        Dict: {
            'success': bool,
            'markdown_file': str (成功時),
            'error': str (エラー時)
        }
    """
    try:
        os.makedirs(output_dir, exist_ok=True)

        # markdownファイル名を生成
        markdown_file = os.path.join(output_dir, f"{paper_id}_translated.md")

        # markdownファイルとして保存
        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write(translated_content)

        return {
            "success": True,
            "markdown_file": markdown_file,
            "file_size": len(translated_content),
        }

    except Exception as e:
        return {"success": False, "error": f"Error saving markdown: {str(e)}"}


def extract_paper_metadata(content: str, file_type: str) -> Dict:
    """
    論文のメタデータを抽出

    Args:
        content: ファイルの内容
        file_type: ファイルタイプ

    Returns:
        Dict: 抽出されたメタデータ
    """
    metadata = {
        "title": None,
        "authors": None,
        "abstract": None,
        "keywords": None,
        "file_type": file_type,
    }

    if file_type == "tex":
        # TeXファイルからメタデータを抽出
        title_match = re.search(r"\\title\{([^}]+)\}", content)
        if title_match:
            metadata["title"] = title_match.group(1).strip()

        author_match = re.search(r"\\author\{([^}]+)\}", content)
        if author_match:
            metadata["authors"] = author_match.group(1).strip()

        # abstract環境を検索
        abstract_match = re.search(
            r"\\begin\{abstract\}(.*?)\\end\{abstract\}", content, re.DOTALL
        )
        if abstract_match:
            metadata["abstract"] = abstract_match.group(1).strip()

        # keywordsを検索
        keywords_match = re.search(r"\\keywords\{([^}]+)\}", content)
        if keywords_match:
            metadata["keywords"] = keywords_match.group(1).strip()

    return metadata


def split_tex_content(content: str, max_chunk_size: int = 8000) -> List[Dict]:
    """
    TeXファイルの内容を適切なサイズに分割

    Args:
        content: TeXファイルの内容
        max_chunk_size: 各チャンクの最大サイズ（文字数）

    Returns:
        List[Dict]: 分割されたチャンクのリスト
    """
    chunks = []

    # セクションのパターンを定義
    section_patterns = [
        r"\\section\{([^}]+)\}",
        r"\\subsection\{([^}]+)\}",
        r"\\subsubsection\{([^}]+)\}",
        r"\\chapter\{([^}]+)\}",
        r"\\begin\{theorem\}",
        r"\\begin\{proof\}",
        r"\\begin\{definition\}",
        r"\\begin\{lemma\}",
        r"\\begin\{corollary\}",
    ]

    # セクションの位置を特定
    section_positions = []
    for pattern in section_patterns:
        for match in re.finditer(pattern, content):
            section_positions.append(
                {
                    "title": match.group(1) if match.groups() else match.group(0),
                    "start": match.start(),
                    "pattern": pattern,
                }
            )

    # 位置でソート
    section_positions.sort(key=lambda x: x["start"])

    # チャンクに分割
    current_chunk = ""
    current_chunk_start = 0
    chunk_index = 1

    for i, section in enumerate(section_positions):
        # 次のセクションの開始位置を取得
        next_start = (
            section_positions[i + 1]["start"]
            if i + 1 < len(section_positions)
            else len(content)
        )

        # 現在のセクションの内容を取得
        section_content = content[section["start"] : next_start]

        # チャンクサイズをチェック
        if len(current_chunk) + len(section_content) > max_chunk_size and current_chunk:
            # 現在のチャンクを保存
            chunks.append(
                {
                    "index": chunk_index,
                    "title": f"Part {chunk_index}",
                    "content": current_chunk.strip(),
                    "start_pos": current_chunk_start,
                    "end_pos": section["start"],
                    "size": len(current_chunk),
                }
            )

            # 新しいチャンクを開始
            current_chunk = section_content
            current_chunk_start = section["start"]
            chunk_index += 1
        else:
            # 現在のチャンクに追加
            current_chunk += section_content

    # 最後のチャンクを追加
    if current_chunk:
        chunks.append(
            {
                "index": chunk_index,
                "title": f"Part {chunk_index}",
                "content": current_chunk.strip(),
                "start_pos": current_chunk_start,
                "end_pos": len(content),
                "size": len(current_chunk),
            }
        )

    # チャンクが1つも作成されなかった場合（セクションが見つからない場合）
    if not chunks:
        # 単純にサイズで分割
        for i in range(0, len(content), max_chunk_size):
            chunk_content = content[i : i + max_chunk_size]
            chunks.append(
                {
                    "index": len(chunks) + 1,
                    "title": f"Part {len(chunks) + 1}",
                    "content": chunk_content,
                    "start_pos": i,
                    "end_pos": min(i + max_chunk_size, len(content)),
                    "size": len(chunk_content),
                }
            )

    return chunks


def merge_translated_chunks(chunks: List[Dict], translated_chunks: List[str]) -> str:
    """
    翻訳されたチャンクを結合

    Args:
        chunks: 元のチャンク情報
        translated_chunks: 翻訳されたチャンクのリスト

    Returns:
        str: 結合された翻訳内容
    """
    if len(chunks) != len(translated_chunks):
        raise ValueError("Chunks and translated chunks count mismatch")

    merged_content = []

    for i, (chunk, translated) in enumerate(zip(chunks, translated_chunks)):
        merged_content.append(f"## {chunk['title']}\n")
        merged_content.append(translated)
        merged_content.append("\n")

    return "\n".join(merged_content)


def create_markdown_template(metadata: Dict, translated_content: str) -> str:
    """
    markdownテンプレートを作成

    Args:
        metadata: 論文のメタデータ
        translated_content: 翻訳されたコンテンツ

    Returns:
        str: markdown形式のテンプレート
    """
    markdown = []

    # タイトル
    if metadata.get("title"):
        markdown.append(f"# {metadata['title']}\n")

    # 著者
    if metadata.get("authors"):
        markdown.append(f"**著者:** {metadata['authors']}\n")

    # 要約
    if metadata.get("abstract"):
        markdown.append("## 要約\n")
        markdown.append(f"{metadata['abstract']}\n")

    # キーワード
    if metadata.get("keywords"):
        markdown.append("## キーワード\n")
        markdown.append(f"{metadata['keywords']}\n")

    # 翻訳されたコンテンツ
    markdown.append("## 翻訳\n")
    markdown.append(translated_content)

    return "\n".join(markdown)


# Google ADK用のツール関数
def translation_file_reader_tool(file_path: str) -> str:
    """
    Google ADK用のツール関数: 翻訳用ファイル読み込み

    Args:
        file_path: ファイルのパス

    Returns:
        str: JSON文字列
    """
    result = read_file_for_translation(file_path)
    return json.dumps(result, ensure_ascii=False, indent=2)


def translation_markdown_saver_tool(
    translated_content: str, paper_id: str, output_dir: str = "agent_outputs"
) -> str:
    """
    Google ADK用のツール関数: 翻訳結果をmarkdown保存

    Args:
        translated_content: 翻訳されたコンテンツ
        output_dir: 出力ディレクトリ
        paper_id: 論文ID

    Returns:
        str: JSON文字列
    """
    result = save_translation_to_markdown(translated_content, paper_id, output_dir)
    return json.dumps(result, ensure_ascii=False, indent=2)


def translation_metadata_extractor_tool(content: str, file_type: str) -> str:
    """
    Google ADK用のツール関数: メタデータ抽出

    Args:
        content: ファイルの内容
        file_type: ファイルタイプ

    Returns:
        str: JSON文字列
    """
    result = extract_paper_metadata(content, file_type)
    return json.dumps(result, ensure_ascii=False, indent=2)


def translation_tex_splitter_tool(content: str, max_chunk_size: int = 8000) -> str:
    """
    Google ADK用のツール関数: TeXファイル分割

    Args:
        content: TeXファイルの内容
        max_chunk_size: 各チャンクの最大サイズ

    Returns:
        str: JSON文字列
    """
    result = split_tex_content(content, max_chunk_size)
    return json.dumps(result, ensure_ascii=False, indent=2)


def translation_chunk_merger_tool(chunks: str, translated_chunks: str) -> str:
    """
    Google ADK用のツール関数: 翻訳チャンク結合

    Args:
        chunks: 元のチャンク情報（JSON文字列）
        translated_chunks: 翻訳されたチャンクのリスト（JSON文字列）

    Returns:
        str: JSON文字列
    """
    try:
        chunks_data = json.loads(chunks)
        translated_data = json.loads(translated_chunks)
        result = merge_translated_chunks(chunks_data, translated_data)
        return json.dumps(
            {"success": True, "merged_content": result}, ensure_ascii=False, indent=2
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)}, ensure_ascii=False, indent=2
        )
