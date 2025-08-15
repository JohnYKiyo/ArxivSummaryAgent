from dotenv import load_dotenv

from src.tools.translation_tools import translate_file_tool

load_dotenv(verbose=True)
load_dotenv(".env")

output = translate_file_tool(
    file_path="agent_outputs/1706.03762/ms_expanded.tex",
    paper_id="1706.03762",
    output_dir="agent_outputs",
)
print(output)
