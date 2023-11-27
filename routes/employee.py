from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from models.employee import employees
from models.employees_per_day import employees_per_day
from config.db import conn
from schemas.employee import Employee
from starlette.status import HTTP_204_NO_CONTENT

employee = APIRouter()


@employee.post("/employee", response_model=Employee, tags=["employees"])
def create_employee(employee: Employee):
    new_employee = {"id": employee.id, "name": employee.name}
    conn.execute(employees.insert().values(**new_employee))
    conn.commit()
    created_employee = conn.execute(employees.select().where(
        employees.c.id == employee.id)).first()
    return created_employee


@employee.get("/employee/{id}", response_model=Employee, tags=["employees"])
def get_employee(id: str):
    result = conn.execute(employees.select().where(
        employees.c.id == id)).first()
    if not result:
        return {"error": "Employee not found"}
    return result


@employee.get("/employee", response_model=list[Employee], tags=["employees"])
def get_employees():
    result = conn.execute(employees.select()).fetchall()
    return result


@employee.delete("/employee/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["employees"])
def delete_employee(id: str):
    result = conn.execute(employees.delete().where(employees.c.id == id))
    if not result.rowcount:
        return {"error": "Employee not found"}
    conn.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)


@employee.put("/employee/{id}", response_model=Employee, tags=["employees"])
def update_employee(id: str, employee: Employee):
    result = conn.execute(employees.update().values(
        name=employee.name).where(employees.c.id == id))
    if not result.rowcount:
        return JSONResponse(status_code=404, content={"detail": "Loan not found"})
    conn.commit()
    return conn.execute(employees.select().where(employees.c.id == id)).first()
