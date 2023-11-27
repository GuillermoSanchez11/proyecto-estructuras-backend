from pydantic import BaseModel
from typing import Optional


class EmployeesPerDay(BaseModel):
    day: str
    daily_tasks: str
    base_employees: int
    employees_quantity: Optional[int]

class EmployeesPerDayPut(BaseModel):
    daily_tasks: str
    base_employees: int
    employees_quantity: Optional[int]
