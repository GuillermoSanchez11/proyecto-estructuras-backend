from pydantic import BaseModel
from typing import Optional


class Book(BaseModel):
    book_id: str
    title: str
    author: str
    genre: str
    year: str
    Suggestion: Optional[int]
    total_loans: Optional[int]
