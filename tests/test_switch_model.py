import asyncio
from typing import Literal

from dotenv import load_dotenv
from google.adk.models import Gemini
from google.adk.models import LlmRequest
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

load_dotenv()


async def get_simple_llm_response(type: Literal["gemini", "gpt"]):
    """純粋なLLM応答を取得するサンプル関数"""

    if type == "gemini":
        llm = Gemini(model="gemini-2.5-flash")
    elif type == "gpt":
        llm = LiteLlm(model="gpt-5-mini")
    else:
        raise ValueError("Invalid type")

    user_prompt = "夏の日本"
    request = LlmRequest(
        model=llm.model,
        contents=[
            types.Content(
                role="user",  # 役割を「ユーザー」に設定
                parts=[types.Part(text=user_prompt)],  # 質問テキストを設定
            )
        ],
        config=types.GenerationConfig(),
    )
    request.append_instructions(
        [
            "あなたは日本の優秀なコピーライターです。",
            "入力されたテーマについて、魅力的で簡潔なキャッチコピーを3つ提案してください。",
        ]
    )

    # 3. generate_content_asyncを呼び出して応答を取得
    print(f"👤 User: {user_prompt}")

    # stream=False (デフォルト) の場合、応答は一度にまとめて返されます。
    response_generator = llm.generate_content_async(request, stream=False)

    async for llm_response in response_generator:
        if llm_response.content:
            # 応答オブジェクトからテキスト部分を抽出
            response_text = llm_response.content.parts[0].text
            print(f"🤖 Model: {response_text}")
        elif llm_response.error_message:
            print(f"エラー: {llm_response.error_message}")


# --- 非同期関数の実行 ---
# 実際にこのコードを実行するには、Google AIのAPIキーを設定する必要があります。
# from google.genai import configure
# configure(api_key="YOUR_API_KEY")
#
if __name__ == "__main__":
    asyncio.run(get_simple_llm_response(type="gemini"))

# 以下は、上記コードの実行結果の例です。
# 👤 User: こんにちは！あなたの名前と役割について教えてください。
# 🤖 Model: こんにちは！私はGoogleによってトレーニングされた、大規模言語モデルです。
