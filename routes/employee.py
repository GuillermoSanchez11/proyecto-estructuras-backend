from fastapi import APIRouter, Response, status
from models.employee import employees
from config.db import conn
from schemas.employee import Employee
from starlette.status import HTTP_204_NO_CONTENT

employee = APIRouter()


@employee.post("/employee", response_model=Employee, tags=["employees"])
def create_employee(employee: Employee):
    new_employee = {"id": employee.id, "name": employee.name}
    print(new_employee)
    result = conn.execute(employees.insert().values(**new_employee))
    conn.commit()
    print(result)
    return conn.execute(employees.select().where(employees.c.id == result.lastrowid)).first()


@employee.get("/employee/{id}", response_model=Employee, tags=["employees"])
def get_employee(id: str):
    result = conn.execute(employees.select().where(
        employees.c.id == id)).first()
    if not result:
        return {"error": "Employee not found"}
    return {"data": {"id": result[0], "name": result[1]}}


@employee.get("/employee", response_model=list[Employee], tags=["employees"])
def get_employees():
    result = conn.execute(employees.select()).fetchall()
    result_dicts = [{"id": (row[0]), "name": row[1]} for row in result]
    response = {"data": result_dicts}
    return response


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
        return {"error": "Employee not found"}
    conn.commit()
    return conn.execute(employees.select().where(employees.c.id == id)).first()
