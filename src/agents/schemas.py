from typing import Literal, Optional

from pydantic import BaseModel


class Metadata(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    published_year: Optional[str] = None
    url: Optional[str] = None


class ArxivFormatOutput(BaseModel):
    status: Literal["success", "error"]
    input_file: str
    file_type: Literal["tex", "pdf"]
    paper_dir: Optional[str] = None
    metadata: Optional[Metadata] = None
