from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from config.db import conn
from models.employees_per_day import employees_per_day
from models.book import books
from models.loan import loans
from schemas.employee import Employee
from schemas.employees_per_day import EmployeesPerDay, EmployeesPerDayPut
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select, text, update

employee_per_day = APIRouter()


@employee_per_day.post("/employees_per_days_per_day", response_model=EmployeesPerDay, tags=["employees_per_day"])
def create_employees_per_day(employee_per_day: EmployeesPerDay):
    if employee_per_day.daily_tasks == "aseo":
        employee_per_day.base_employees = 3
    elif employee_per_day.daily_tasks == "inventario":
        employee_per_day.base_employees = 2
    else:
        employee_per_day.base_employees = 0

    new_employee_per_day = {
        "day": employee_per_day.day,
        "daily_tasks": employee_per_day.daily_tasks,
        "base_employees": employee_per_day.base_employees,
        "employees_quantity": None
    }

    conn.execute(employees_per_day.insert().values(new_employee_per_day))
    conn.commit()

    created_employee_per_day = conn.execute(employees_per_day.select().where(
        employees_per_day.c.day == employee_per_day.day)).first()

    return created_employee_per_day


@employee_per_day.get("/employees_per_day/{day}", response_model=EmployeesPerDay, tags=["employees_per_day"])
def get_employees_per_day(day: str):
    result = conn.execute(employees_per_day.select().where(

        employees_per_day.c.day == day)).first()
    if not result:
        return {"error": "Entry not found"}
    return result


@employee_per_day.get("/employees_per_day", response_model=list[EmployeesPerDay], tags=["employees_per_day"])
def get_all_employees_per_day():
    result = conn.execute(employees_per_day.select()).fetchall()
    return result


@employee_per_day.delete("/employees_per_day/{day}", status_code=status.HTTP_204_NO_CONTENT, tags=["employees_per_day"])
def delete_employees_per_day(day: str):
    result = conn.execute(employees_per_day.delete().where(
        employees_per_day.c.day == day))
    if not result.rowcount:
        return {"error": "Entry not found"}
    conn.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)


def get_day_of_week(loan_date):
    return loan_date.strftime("%A")


def update_days():
    loans_list = conn.execute(loans.select()).fetchall()

    days_count = {"Monday": 0, "Tuesday": 0, "Wednesday": 0,
                  "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0}

    for loan in loans_list:
        loan_date = loan[4]
        day_of_week = get_day_of_week(loan_date)

        update_statement = update(loans).values(
            week_day=day_of_week).where(loans.c.id == loan[0])
        conn.execute(update_statement)

        days_count[day_of_week] += 1

    conn.commit()
    print("Days count:", days_count)

    return days_count


@employee_per_day.put("/employees_per_day/{day}", response_model=EmployeesPerDayPut, tags=["employees_per_day"])
def update_employees_per_day(day: str, employee_per_day: EmployeesPerDay):

    if employee_per_day.daily_tasks == "aseo":
        employee_per_day.base_employees = 3
    elif employee_per_day.daily_tasks == "inventario":
        employee_per_day.base_employees = 2
    else:
        employee_per_day.base_employees = 0

    # Actualizar la cantidad de empleados en el diccionario days_count
    days_count = update_days()
    print(day)
    print(type(day))

    # Aplicar la lógica específica para calcular employees_quantity
    if day in days_count:
        days_value = days_count[day]
        additional_employees = days_value // 150
        employee_per_day.employees_quantity = (
            employee_per_day.base_employees + additional_employees
        )

        # Actualizar la entrada en la base de datos con la nueva employees_quantity
        result = conn.execute(employees_per_day.update().values(
            daily_tasks=employee_per_day.daily_tasks,
            base_employees=employee_per_day.base_employees,
            employees_quantity=employee_per_day.employees_quantity
        ).where(employees_per_day.c.day == day))
        print(conn.execute(employees_per_day.select().where(
            employees_per_day.c.day == day)).first())
        conn.commit()

        if not result.rowcount:
            return JSONResponse(status_code=404, content={"detail": "Loan not found"})
        conn.commit()
        return conn.execute(employee_per_day.select().where(loans.c.id == id)).first()
