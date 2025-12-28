from typing import List, Optional
from pydantic import BaseModel


class StationConfig(BaseModel):
    parser_type: str
    skip_if_contains: List[str]
    delimiter: Optional[str] = None
    artist_first: Optional[bool] = True
    pattern: Optional[str] = None
    field_mapping: Optional[List[str]] = None
