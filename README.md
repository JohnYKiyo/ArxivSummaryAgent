# arXiv Summary Agent

arXiv 論文の自動翻訳・要約システムです。Google ADK の SequentialAgent を使用して、URL を入力するだけで、論文を日本語に翻訳し、論文タイプに応じた要約を生成します。

## 機能

- 📥 arXiv URL から論文の tex ファイルを自動ダウンロード
- 🔍 LLM によるメインファイル特定と分析
- 🌐 論文の日本語翻訳（LLM 使用）
- 📝 論文タイプに応じた要約フォーマット生成
- 📄 Markdown 形式での出力
- 🔄 SequentialAgent による自動ワークフロー

## アーキテクチャ

### SequentialAgent ワークフロー

1. **arxiv_agent**: 論文ダウンロード、メインファイル特定、翻訳戦略決定
2. **translation_agent**: 論文翻訳、メタデータ抽出、markdown 保存

### 使用方法

```python
from arxiv.agent import root_agent

# arXiv URLを指定して実行
result = root_agent.run("https://arxiv.org/abs/1706.03762")
```

## ライセンス

MIT License
