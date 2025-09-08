"""arXiv paper fetching and downloading tools."""

import json
import os
import tarfile
from typing import Dict
from typing import Optional
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
