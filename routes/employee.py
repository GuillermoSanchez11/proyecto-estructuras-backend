from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from models.employee import employees
from models.employees_per_day import employees_per_day
from config.db import conn, engine
from schemas.employee import Employee
from starlette.status import HTTP_204_NO_CONTENT

employee = APIRouter()


@employee.post("/employee", response_model=Employee, tags=["employees"])
def create_employee(employee: Employee):
    with engine.connect() as connection:
        new_employee = {"id": employee.id, "name": employee.name}
        connection.execute(employees.insert().values(**new_employee))
        connection.commit()
        created_employee = connection.execute(employees.select().where(
            employees.c.id == employee.id)).first()

    return created_employee


@employee.get("/employee/{id}", response_model=Employee, tags=["employees"])
def get_employee(id: str):
    with engine.connect() as connection:
        result = connection.execute(employees.select().where(
            employees.c.id == id)).first()

    if not result:
        return {"error": "Employee not found"}
    return result


@employee.get("/employee", response_model=list[Employee], tags=["employees"])
def get_employees():
    with engine.connect() as connection:
        result = connection.execute(employees.select()).fetchall()
    return result


@employee.delete("/employee/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["employees"])
def delete_employee(id: str):
    with engine.connect() as connection:
        result = connection.execute(
            employees.delete().where(employees.c.id == id))
        connection.commit()
    if not result.rowcount:
        return {"error": "Employee not found"}

    return Response(status_code=HTTP_204_NO_CONTENT)


@employee.put("/employee/{id}", response_model=Employee, tags=["employees"])
def update_employee(id: str, employee: Employee):
    with engine.connect() as connection:
        result = connection.execute(employees.update().values(
            name=employee.name).where(employees.c.id == id))
        connection.commit()
        employee_updated = connection.execute(employees.select().where(
            employees.c.id == id)).first()
    if not result.rowcount:
        return JSONResponse(status_code=404, content={"detail": "Loan not found"})

    return employee_updated
