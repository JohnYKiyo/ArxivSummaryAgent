"""Arxiv agent tools for paper processing."""

import json
import os
import re
import tarfile
from typing import Dict, Optional
from urllib.parse import urlparse

import arxiv


def _fetch_eprint_from_arxiv(url: str, output_dir: str = "agent_outputs") -> Dict:
    """
    Arxiv URLからe-printファイル一式をダウンロードする

    Args:
        url: Arxiv論文のURL
        output_dir: 保存先ディレクトリ

    Returns:
        Dict: {
            'success': bool,
            'paper_dir': str (成功時),
            'files': List[str] (成功時),
            'error': str (エラー時)
        }
    """
    try:
        # URLから論文IDを抽出
        arxiv_id = _extract_arxiv_id(url)
        if not arxiv_id:
            return {"success": False, "error": "Invalid Arxiv URL"}

        # 出力ディレクトリを作成
        paper_dir = os.path.join(output_dir, arxiv_id)
        os.makedirs(paper_dir, exist_ok=True)

        # arxivライブラリを使って論文を検索
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())

        # ソースファイルをダウンロード
        paper.download_source(dirpath=paper_dir, filename=f"{arxiv_id}.tar.gz")

        # tarファイルを展開
        tar_path = os.path.join(paper_dir, f"{arxiv_id}.tar.gz")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=paper_dir)

        # tarファイルを削除
        os.remove(tar_path)

        # 展開されたファイル一覧を取得
        files = []
        for root, _, filenames in os.walk(paper_dir):
            for filename in filenames:
                files.append(os.path.join(root, filename))

        if not files:
            return {"success": False, "error": "No files found after extraction"}

        return {"success": True, "paper_dir": paper_dir, "files": files}

    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def _extract_arxiv_id(url: str) -> Optional[str]:
    """URLから論文IDを抽出"""
    try:
        parsed = urlparse(url)
        if parsed.netloc not in ["arxiv.org", "www.arxiv.org"]:
            return None

        path = parsed.path.strip("/")
        if not path.startswith("abs/"):
            return None

        # abs/を除去して論文IDを取得
        paper_id = path[4:]

        # バージョン部分を除去 (例: 1706.03762v6 -> 1706.03762)
        if "v" in paper_id:
            paper_id = paper_id.split("v")[0]

        return paper_id
    except Exception:
        return None


# Google ADK用のツール関数
def arxiv_eprint_fetcher_tool(
    url: str, output_dir: Optional[str] = "agent_outputs"
) -> str:
    """
    Google ADK用のツール関数: Arxivからe-printファイル一式を取得

    Args:
        url: Arxiv論文のURL
        output_dir: 保存先ディレクトリ（Noneの場合は"agent_outputs"を使用）

    Returns:
        str: JSON文字列
    """
    result = _fetch_eprint_from_arxiv(url, output_dir)

    if result["success"]:
        # ファイルの種類を分類
        tex_files = [f for f in result["files"] if f.endswith(".tex")]
        pdf_files = [f for f in result["files"] if f.endswith(".pdf")]
        other_files = [f for f in result["files"] if not f.endswith((".tex", ".pdf"))]

        summary = {
            "status": "success",
            "paper_dir": result["paper_dir"],
            "total_files": len(result["files"]),
            "tex_files": len(tex_files),
            "pdf_files": len(pdf_files),
            "other_files": len(other_files),
            "files": [os.path.basename(f) for f in result["files"]],
        }
    else:
        summary = {"status": "error", "error": result["error"]}

    return json.dumps(summary, ensure_ascii=False, indent=2)


def get_all_files(paper_dir: str) -> Dict:
    """
    論文ディレクトリ内のすべてのファイルを取得

    Args:
        paper_dir: 論文ファイルが保存されているディレクトリ

    Returns:
        Dict: {
            'success': bool,
            'files': List[str] (成功時),
            'error': str (エラー時)
        }
    """
    try:
        if not os.path.exists(paper_dir):
            return {"success": False, "error": f"Directory not found: {paper_dir}"}

        # すべてのファイルを再帰的に取得
        all_files = []
        for root, dirs, files in os.walk(paper_dir):
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)

        if not all_files:
            return {"success": False, "error": "No files found in directory"}

        # ファイルの種類を分類
        tex_files = [f for f in all_files if f.endswith(".tex")]
        pdf_files = [f for f in all_files if f.endswith(".pdf")]
        other_files = [f for f in all_files if not f.endswith((".tex", ".pdf"))]

        return {
            "success": True,
            "files": all_files,
            "tex_files": tex_files,
            "pdf_files": pdf_files,
            "other_files": other_files,
        }

    except Exception as e:
        return {"success": False, "error": f"Error getting files: {str(e)}"}


def _read_file_content(file_path: str) -> Dict:
    """
    ファイルの内容を読み込む

    Args:
        file_path: ファイルのパス

    Returns:
        Dict: {
            'success': bool,
            'content': str (成功時),
            'file_size': int (成功時),
            'error': str (エラー時)
        }
    """
    try:
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}

        file_size = os.path.getsize(file_path)

        # ファイルの種類に応じて読み込み方法を変更
        if file_path.endswith(".tex"):
            # TeXファイルはテキストとして読み込み
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        elif file_path.endswith(".pdf"):
            # PDFファイルはバイナリとして読み込み（サイズ情報のみ）
            content = f"[PDF file - {file_size} bytes]"
        else:
            # その他のファイルはテキストとして試行
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except UnicodeDecodeError:
                content = f"[Binary file - {file_size} bytes]"

        return {
            "success": True,
            "content": content,
            "file_size": file_size,
            "file_path": file_path,
        }

    except Exception as e:
        return {"success": False, "error": f"Error reading file: {str(e)}"}


def _expand_tex_file(tex_file_path: str, output_dir: Optional[str] = None) -> Dict:
    """
    TeXファイルのinput文を展開して1つのファイルにする

    Args:
        tex_file_path: メインTeXファイルのパス
        output_dir: 出力ディレクトリ（Noneの場合は元ファイルと同じディレクトリ）

    Returns:
        Dict: {
            'success': bool,
            'expanded_file': str (成功時),
            'error': str (エラー時)
        }
    """
    try:
        if not os.path.exists(tex_file_path):
            return {"success": False, "error": f"TeX file not found: {tex_file_path}"}

        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = os.path.dirname(tex_file_path)

        os.makedirs(output_dir, exist_ok=True)

        # 元のファイルを読み込み
        with open(tex_file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # \input文を検索して展開
        expanded_content = _expand_input_statements(
            content, os.path.dirname(tex_file_path)
        )

        # 展開されたファイルを保存
        base_name = os.path.splitext(os.path.basename(tex_file_path))[0]
        expanded_file_path = os.path.join(output_dir, f"{base_name}_expanded.tex")

        with open(expanded_file_path, "w", encoding="utf-8") as f:
            f.write(expanded_content)

        return {
            "success": True,
            "expanded_file": expanded_file_path,
            "original_file": tex_file_path,
            "content_length": len(expanded_content),
        }

    except Exception as e:
        return {"success": False, "error": f"Error expanding TeX file: {str(e)}"}


def _expand_input_statements(content: str, base_dir: str) -> str:
    """input文を再帰的に展開"""
    # \input{filename} または \input filename のパターンを検索
    input_patterns = [
        r"\\input\{([^}]+)\}",  # \input{filename}
        r"\\input\s+([^\s\\]+)",  # \input filename
        r"\\include\{([^}]+)\}",  # \include{filename}
    ]

    expanded_content = content

    for pattern in input_patterns:
        matches = re.finditer(pattern, expanded_content)
        for match in reversed(list(matches)):  # 後ろから処理してインデックスを保持
            input_file = match.group(1)

            # 拡張子がない場合は.texを追加
            if not input_file.endswith(".tex"):
                input_file += ".tex"

            # ファイルパスを構築
            input_path = os.path.join(base_dir, input_file)

            # ファイルが存在する場合のみ展開
            if os.path.exists(input_path):
                try:
                    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
                        included_content = f.read()

                    # 再帰的に展開
                    included_content = _expand_input_statements(
                        included_content, base_dir
                    )

                    # 元の\input文を置換
                    expanded_content = (
                        expanded_content[: match.start()]
                        + included_content
                        + expanded_content[match.end() :]
                    )
                except Exception as e:
                    print(f"Warning: Could not expand {input_file}: {e}")

    return expanded_content


# Google ADK用のツール関数
def arxiv_file_lister_tool(paper_dir: str) -> str:
    """
    Google ADK用のツール関数: ファイル一覧取得

    Args:
        paper_dir: 論文ディレクトリのパス

    Returns:
        str: JSON文字列
    """
    result = get_all_files(paper_dir)
    return json.dumps(result, ensure_ascii=False, indent=2)


def arxiv_file_reader_tool(file_path: str) -> str:
    """
    Google ADK用のツール関数: ファイル内容読み込み

    Args:
        file_path: ファイルのパス

    Returns:
        str: JSON文字列
    """
    result = _read_file_content(file_path)
    return json.dumps(result, ensure_ascii=False, indent=2)


def arxiv_tex_expander_tool(
    tex_file_path: str, output_dir: Optional[str] = None
) -> str:
    """
    Google ADK用のツール関数: TeXファイル展開(TeXファイルのinput文を展開して1つのファイルにする)

    Args:
        tex_file_path: TeXファイルのパス
        output_dir: 出力ディレクトリ

    Returns:
        str: JSON文字列
    """
    result = _expand_tex_file(tex_file_path, output_dir)
    return json.dumps(result, ensure_ascii=False, indent=2)


def arxiv_metadata_fetcher_tool(paper_id: str) -> str:
    """
    Fetches metadata for a given arXiv paper ID.

    Args:
        paper_id: The arXiv paper ID (e.g., "1706.03762").

    Returns:
        A JSON string containing the paper's metadata (title, authors, summary, published date).
    """
    try:
        search = arxiv.Search(id_list=[paper_id])
        paper = next(search.results())

        authors = [author.name for author in paper.authors]

        metadata = {
            "title": paper.title,
            "authors": ", ".join(authors),
            "published_year": str(paper.published.year),
            "url": paper.entry_id,
        }
        return json.dumps(
            {"success": True, "metadata": metadata}, ensure_ascii=False, indent=2
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)}, ensure_ascii=False, indent=2
        )
