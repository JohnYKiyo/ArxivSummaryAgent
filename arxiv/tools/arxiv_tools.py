"""Arxiv API tools for fetching e-print files."""

import io
import os
import tarfile
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests


def fetch_eprint_from_arxiv(url: str, output_dir: str = "papers") -> Dict:
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

        # e-printファイルをダウンロード
        eprint_url = f"https://arxiv.org/e-print/{arxiv_id}"
        response = requests.get(eprint_url, timeout=30)
        response.raise_for_status()

        # コンテンツタイプを確認
        content_type = response.headers.get("content-type", "")

        if (
            "application/x-eprint-tar" in content_type
            or "application/gzip" in content_type
        ):
            # tar.gzファイルの場合
            files = _extract_eprint_from_tar(response.content, paper_dir)
        elif "text/plain" in content_type or "application/octet-stream" in content_type:
            # 直接ファイルの場合
            files = _save_single_file(response.text, paper_dir, arxiv_id)
        else:
            return {
                "success": False,
                "error": f"Unexpected content type: {content_type}",
            }

        if not files:
            return {"success": False, "error": "No files found"}

        return {"success": True, "paper_dir": paper_dir, "files": files}

    except requests.RequestException as e:
        return {"success": False, "error": f"Network error: {str(e)}"}
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


def _extract_eprint_from_tar(tar_content: bytes, output_dir: str) -> List[str]:
    """tar.gzファイルからe-printファイル一式を抽出して保存"""
    files = []
    try:
        with tarfile.open(fileobj=io.BytesIO(tar_content), mode="r:gz") as tar:
            # すべてのファイルを抽出
            for member in tar.getmembers():
                # ファイルでない場合はスキップ
                if not member.isfile():
                    continue

                # ファイルを読み込む
                f = tar.extractfile(member)
                if f is None:
                    continue

                try:
                    content = f.read()
                finally:
                    f.close()

                # ディレクトリ構造を保持してファイルパスを作成
                filepath = os.path.join(output_dir, member.name)

                # ディレクトリが存在しない場合は作成
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                # テキストファイルの場合はUTF-8でデコード
                try:
                    text_content = content.decode("utf-8", errors="ignore")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(text_content)
                except UnicodeDecodeError:
                    # バイナリファイルの場合はそのまま保存
                    with open(filepath, "wb") as f:
                        f.write(content)

                files.append(filepath)

    except Exception as e:
        print(f"Error extracting e-print from tar: {e}")

    return files


def _save_single_file(content: str, output_dir: str, arxiv_id: str) -> List[str]:
    """単一のファイルを保存"""
    filename = f"{arxiv_id}.tex"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return [filepath]


# Google ADK用のツール関数
def arxiv_eprint_fetcher_tool(url: str, output_dir: str = "papers") -> str:
    """
    Google ADK用のツール関数: Arxivからe-printファイル一式を取得

    Args:
        url: Arxiv論文のURL
        output_dir: 保存先ディレクトリ

    Returns:
        str: JSON文字列
    """
    import json

    result = fetch_eprint_from_arxiv(url, output_dir)

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
