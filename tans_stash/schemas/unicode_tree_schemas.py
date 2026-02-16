from pydantic import BaseModel
from typing import Optional

class UnicodeTreeBase(BaseModel):
    unicode_tree: str

class UnicodeTreeProcess(UnicodeTreeBase):
    pass