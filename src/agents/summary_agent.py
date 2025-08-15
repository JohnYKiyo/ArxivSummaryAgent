from google.adk.agents import Agent

from src.tools.summary_agent_tools import load_file_tool, summary_tool

INSTRUCTION = """
あなたは論文の要約を作成するエージェントです。
対象のファイルを load_file_tool で読み込んでください。
その後、レビュー/サマリー論文か通常論文かを判断して、summary_tool で要約してください。
レビュー論文/サマリー論文の場合は type に "review" を指定してください。
通常論文の場合は type に "normal" を指定してください。
"""

summary_agent = Agent(
    name="summary_agent",
    model="gemini-2.5-flash",
    description="論文の要約を作成するエージェント",
    instruction=INSTRUCTION,
    tools=[
        summary_tool,
        load_file_tool,
    ],
    output_key="summary_result",
)
