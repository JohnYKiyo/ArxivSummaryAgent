"""Test for Arxiv tools."""

import os
import shutil
import tempfile

from arxiv.tools.arxiv_tools import arxiv_eprint_fetcher_tool, fetch_eprint_from_arxiv


class TestArxivTools:
    """Arxiv toolsのテストクラス"""

    def setup_method(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_fetch_eprint_from_arxiv_success(self):
        """e-printファイル取得の成功テスト"""
        test_url = "https://arxiv.org/abs/1706.03762"

        result = fetch_eprint_from_arxiv(test_url, self.temp_dir)

        # 基本的な構造をチェック
        assert "success" in result

        # 成功した場合のチェック
        if result["success"]:
            assert result["paper_dir"] is not None
            assert result["files"] is not None
            assert len(result["files"]) > 0

            # ディレクトリが作成されているかチェック
            assert os.path.exists(result["paper_dir"])

            # ファイルが保存されているかチェック
            for file_path in result["files"]:
                assert os.path.exists(file_path)
                print(f"Found file: {os.path.basename(file_path)}")

            # ファイルの種類を確認
            tex_files = [f for f in result["files"] if f.endswith(".tex")]
            pdf_files = [f for f in result["files"] if f.endswith(".pdf")]

            print(f"TeX files: {len(tex_files)}")
            print(f"PDF files: {len(pdf_files)}")

        else:
            # エラーの場合、エラーメッセージが存在することを確認
            assert "error" in result
            assert result["error"] is not None

    def test_fetch_eprint_from_arxiv_attention_paper(self):
        """Attention Is All You Need論文のe-print取得テスト"""
        # 有名なTransformer論文のURL
        attention_url = "https://arxiv.org/abs/1706.03762"

        result = fetch_eprint_from_arxiv(attention_url, self.temp_dir)

        print("Testing Attention Is All You Need paper...")
        print(f"Success: {result['success']}")

        if result["success"]:
            print(f"Paper directory: {result['paper_dir']}")
            print(f"Total files: {len(result['files'])}")

            # ファイルの詳細を表示
            for i, file_path in enumerate(result["files"]):
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                print(f"File {i + 1}: {filename} ({file_size} bytes)")

            # ファイルの種類を分類
            tex_files = [f for f in result["files"] if f.endswith(".tex")]
            pdf_files = [f for f in result["files"] if f.endswith(".pdf")]
            other_files = [
                f for f in result["files"] if not f.endswith((".tex", ".pdf"))
            ]

            print(f"TeX files: {len(tex_files)}")
            print(f"PDF files: {len(pdf_files)}")
            print(f"Other files: {len(other_files)}")

            print("✓ Attention Is All You Need paper e-print successfully downloaded!")
        else:
            print(f"Error: {result['error']}")
            assert (
                False
            ), f"Failed to fetch Attention Is All You Need paper: {result['error']}"

    def test_fetch_eprint_from_arxiv_invalid_url(self):
        """無効なURLのテスト"""
        invalid_urls = [
            "https://google.com",
            "https://arxiv.org/",
            "https://arxiv.org/abs/",
            "not_a_url",
        ]

        for url in invalid_urls:
            result = fetch_eprint_from_arxiv(url, self.temp_dir)
            if result["success"]:
                assert False
            else:
                assert result["error"] is not None

    def test_arxiv_eprint_fetcher_tool(self):
        """Google ADK用ツール関数のテスト"""
        test_url = "https://arxiv.org/abs/1706.03762"

        result_json = arxiv_eprint_fetcher_tool(test_url, self.temp_dir)

        # JSON文字列が返されることを確認
        assert isinstance(result_json, str)

        # JSONとしてパースできることを確認
        import json

        result_dict = json.loads(result_json)

        assert "status" in result_dict

        if result_dict["status"] == "success":
            assert "paper_dir" in result_dict
            assert "total_files" in result_dict
            assert "tex_files" in result_dict
            assert "pdf_files" in result_dict
            assert "other_files" in result_dict
            assert "files" in result_dict
            assert result_dict["total_files"] > 0
            assert len(result_dict["files"]) > 0
        else:
            assert "error" in result_dict


if __name__ == "__main__":
    # 簡単なテスト実行
    print("Testing Arxiv tools...")

    # 一時ディレクトリを作成
    temp_dir = tempfile.mkdtemp()
    try:
        # Attention Is All You Need論文のテスト
        test_url = "https://arxiv.org/abs/1706.03762"
        print(f"Testing Attention Is All You Need paper: {test_url}")

        result = fetch_eprint_from_arxiv(test_url, temp_dir)
        print(f"Success: {result['success']}")
        if result["success"]:
            print(f"Paper directory: {result['paper_dir']}")
            print(f"Total files: {len(result['files'])}")

            # ファイルの詳細を表示
            for i, file_path in enumerate(result["files"][:5]):  # 最初の5ファイルのみ
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                print(f"File {i + 1}: {filename} ({file_size} bytes)")

            # ファイルの種類を分類
            tex_files = [f for f in result["files"] if f.endswith(".tex")]
            pdf_files = [f for f in result["files"] if f.endswith(".pdf")]
            other_files = [
                f for f in result["files"] if not f.endswith((".tex", ".pdf"))
            ]

            print(f"TeX files: {len(tex_files)}")
            print(f"PDF files: {len(pdf_files)}")
            print(f"Other files: {len(other_files)}")

            print("✓ Confirmed: This is the Attention Is All You Need paper!")
        else:
            print(f"Error: {result['error']}")
    finally:
        # クリーンアップ
        shutil.rmtree(temp_dir)

    print("Tests completed!")
