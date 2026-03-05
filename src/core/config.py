import os

from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()


class Config:
    """アプリケーションの設定を管理するクラス"""

    # モデル設定
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

    # APIキー設定
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# グローバルな設定インスタンス
config = Config()
