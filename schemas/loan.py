from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Loan(BaseModel):
    id: str
    employee_id: str
    user_name: str
    book: str
    loan_date: datetime
    devolution_date: datetime
    return_date: datetime


class LoanPut(BaseModel):
    devolution_date: Optional[datetime]
    return_date: Optional[datetime]
