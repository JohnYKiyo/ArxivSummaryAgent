from google.adk.agents import Agent

from arxiv.agents.coordinator_agent import coordinator_agent
from arxiv.instructions.utils import load_instruction


def process_arxiv_paper_request(url: str) -> dict:
    """Process arXiv paper request using multi-agent system"""
    # SequentialAgentを使用してワークフローを実行
    result = coordinator_agent.run(f"arXiv論文の処理を開始してください。URL: {url}")
    return result


main_agent = Agent(
    name="arxiv_main_agent",
    model="gemini-2.0-flash",
    description="arXiv論文要約システムのメインエージェント",
    instruction=load_instruction("main_agent_instructions.txt"),
    tools=[process_arxiv_paper_request],
)
