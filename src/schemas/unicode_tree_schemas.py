from pydantic import BaseModel

class UnicodeTreeBase(BaseModel):
    unicode_tree: str

class UnicodeTreeProcess(UnicodeTreeBase):
    pass