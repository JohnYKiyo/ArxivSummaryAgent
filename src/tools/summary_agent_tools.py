import os


def read_file_tool(file_path: str) -> str:
    """Read the content of a file.

    Args:
        file_path: The path to the file to read.

    Returns:
        The content of the file as a string, or an error message if it fails.
    """
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
