from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Loan(BaseModel):
    id: str
    employee_id: str
    user_name: str
    book_id: str
    loan_date: datetime
    devolution_date: Optional[datetime]
    return_date: Optional[datetime]
    week_day: Optional[str]


class LoanPut(BaseModel):
    devolution_date: Optional[datetime]
    return_date: Optional[datetime]


class LoanReturn(BaseModel):
    return_date: Optional[datetime]
