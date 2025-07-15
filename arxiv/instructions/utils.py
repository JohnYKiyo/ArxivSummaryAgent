import os


def load_instruction(file_name: str) -> str:
    """Load instruction from file"""
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"指示ファイルが見つかりません: {file_name}"
    except Exception as e:
        return f"指示ファイルの読み込みに失敗しました: {str(e)}"
