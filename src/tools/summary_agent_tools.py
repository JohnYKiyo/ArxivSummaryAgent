import os
from typing import Literal

from src.tools.llm.llm_model import call_model

REVIEW_INSTRUCTION = """
あなたはレビュー/サーベイ論文の要約を作成するエージェントです。
下記のフォーマットに従って要約を作成してください。

フォーマット:
# [論文のタイトルをここに記入 - タイトルは原文のまま出力]

URL: [論文 URL をここに記入]

発表年: [発表された年をここに記入]

著者:

[著者の名前をここに記入]

著者の所属機関:

[著者の所属する組織や機関をここに記入]

## 要約

[論文の目的、主要な内容、結果、および結論を簡潔にまとめてここに記入]

## レビュー/サーベイ項目

[論文で提案されたレビュー内容/サーベイ内容を箇条書きでここに記入]

## 比較

[それぞれのレビュー内容/サーベイ内容をまとめてください。]
[論文内で使われている比較表などを含めてください。]

## 議論

[論文の結果や結論に関する議論、今後の研究課題、さらなる研究の可能性などをここに記述]
"""

NORMAL_INSTRUCTION = """
あなたは論文の要約を作成するエージェントです。
下記のフォーマットに従って要約を作成してください。

フォーマット:
# [論文のタイトルをここに記入 - タイトルは原文のまま出力]

URL: [論文 URL をここに記入]

発表年: [発表された年をここに記入]

著者:

[著者の名前をここに記入]

著者の所属機関:

[著者の所属する組織や機関をここに記入]

## 要約

[論文の主要な内容、結果、および結論を簡潔にまとめてここに記入]

## 使用された手法

[論文で使用された新しい手法や技術をここに簡潔に記入]

## 技術の主要なポイント

[論文で提案された技術の主要なポイントや特徴を箇条書きでここに記入]

## 先行研究との比較

[この論文の技術やアプローチが先行研究と比較してどのような利点や新規性を持っているかをここに記述]

## 実験方法

[論文で行われた実験や研究の方法をここに記述]

## 議論

[論文の結果や結論に関する議論、今後の研究課題、さらなる研究の可能性などをここに記述]
"""


def summary_tool(
    content_file_path: str,
    output_file_path: str,
    output_dir: str,
    type: Literal["review", "normal"],
) -> str:
    """
    Summarize the content of a file.

    Args:
        content_file_path: The path to the file to review.
        output_file_path: The path to the file to save the summary.
        output_dir: The directory to save the file in.
        type: The type of the file to review.

    Returns:
        The summary of the content of the file as a string, or an error message if it fails.
    """

    try:
        content_to_summary = load_file_tool(content_file_path)
    except Exception as e:
        return f"Error reading file at {content_file_path}: {e}"

    if type == "review":
        summary = call_model(
            [content_to_summary], system_instruction=REVIEW_INSTRUCTION
        )
    elif type == "normal":
        summary = call_model(
            [content_to_summary], system_instruction=NORMAL_INSTRUCTION
        )
    else:
        return f"Invalid type: {type}"

    text = save_markdown_tool(output_dir, output_file_path, summary)
    return text


def load_file_tool(file_path: str) -> str:
    """Load the content of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file at {file_path}: {e}"


def save_markdown_tool(output_dir: str, file_path: str, markdown_content: str) -> str:
    """Save the markdown content to a file.

    Args:
        output_dir: The directory to save the file in.
        file_path: The name of the file to save.
        markdown_content: The markdown content to save.

    Returns:
        A message indicating the result of the save operation.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(output_dir, file_path)
        with open(full_path, "w") as f:
            f.write(markdown_content)
        return f"Successfully saved markdown to {full_path}"
    except Exception as e:
        return f"Error saving markdown to {full_path}: {e}"
