from fastapi import APIRouter
from models.employee import employees
from config.db import conn
from schemas.employee import Employee

employee = APIRouter()


@employee.get("/employee")
def get_employees():
    return conn.execute(employees.select()).fetchall()


@employee.post("/employee")
def create_employee(employee: Employee):
    new_employee = {"id": employee.id, "name": employee.name}
    print(new_employee)
    result = conn.execute(employees.insert().values(**new_employee))
    conn.commit()
    print(result)
    return {"message": "Employee created!"}
