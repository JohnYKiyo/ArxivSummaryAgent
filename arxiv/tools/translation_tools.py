"""Translation tools for arXiv papers."""

import json
import os
import re
from typing import Dict, List, Optional

from arxiv.tools.llm_model import call_model
from arxiv.tools.prompt import TRANSLATION_INSTRUCTION


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


def split_tex_content(content: str, max_chunk_size: int = 10000) -> List[Dict]:
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


def _append_translation_to_markdown(
    translated_chunk: str,
    paper_id: str,
    output_dir: str = "agent_outputs",
) -> Dict:
    """
    翻訳されたチャンクをmarkdownファイルに追記する

    Args:
        translated_chunk: 翻訳されたチャンクのコンテンツ
        paper_id: 論文ID
        output_dir: 出力ディレクトリ

    Returns:
        Dict: {
            'success': bool,
            'markdown_file': str (成功時),
            'error': str (エラー時)
        }
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        markdown_file = os.path.join(output_dir, f"{paper_id}_translated.md")
        content_to_append = f"\n\n{translated_chunk}\n\n"
        with open(markdown_file, "a", encoding="utf-8") as f:
            f.write(content_to_append)
        return {
            "success": True,
            "markdown_file": markdown_file,
        }
    except Exception as e:
        return {"success": False, "error": f"Error appending to markdown: {str(e)}"}


def process_and_translate_chunks(
    chunks: list, paper_id: str, output_dir: str = "agent_outputs"
) -> Dict:
    """
    受け取ったチャンクのリストをループ処理し、翻訳してMarkdownファイルに追記する。
    ADK Agentの代わりにgoogle-generativeaiを直接呼び出す。
    """
    print("process_and_translate_chunks started.")
    try:
        markdown_file = os.path.join(output_dir, f"{paper_id}_translated.md")

        os.makedirs(output_dir, exist_ok=True)
        if os.path.exists(markdown_file):
            os.remove(markdown_file)

        print(f"Loaded {len(chunks)} chunks. Starting translation loop...")

        for i, chunk in enumerate(chunks):
            content_to_translate = chunk.get("content")
            chunk_title = chunk.get("title", f"Part {chunk.get('index', i + 1)}")

            if not content_to_translate:
                continue

            print(f"Processing chunk {i + 1}/{len(chunks)}: '{chunk_title}'")
            translated_chunk = call_model(
                content_to_translate, system_instruction=TRANSLATION_INSTRUCTION
            )

            _append_translation_to_markdown(
                translated_chunk=translated_chunk,
                paper_id=paper_id,
                output_dir=output_dir,
            )

        print("All chunks processed successfully.")
        return {"success": True, "file": markdown_file}

    except Exception as e:
        import traceback

        print(f"An error occurred in process_and_translate_chunks: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def translate_file_tool(
    file_path: str, paper_id: str, output_dir: Optional[str] = "agent_outputs"
) -> str:
    """
    Google ADK用のツール関数: 翻訳
    """
    readfile = read_file_for_translation(file_path)
    if not readfile["success"]:
        return json.dumps(
            {"success": False, "error": readfile["error"]},
            ensure_ascii=False,
            indent=2,
        )

    split = split_tex_content(readfile["content"])
    output = process_and_translate_chunks(split, paper_id, output_dir)

    return json.dumps(output, ensure_ascii=False, indent=2)
