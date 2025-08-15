from dotenv import load_dotenv

from arxiv.tools.translation_tools import (
    process_and_translate_chunks,
    translation_file_reader_tool,
    translation_tex_splitter_tool,
)

load_dotenv(verbose=True)
load_dotenv(".env")

readfile = translation_file_reader_tool("agent_outputs/1706.03762/ms_expanded.tex")

split = translation_tex_splitter_tool(readfile)

output = process_and_translate_chunks(split, "test")
print(output)
