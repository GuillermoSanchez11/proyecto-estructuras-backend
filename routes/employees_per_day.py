from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from config.db import conn, engine
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
    with engine.connect() as connection:
        if employee_per_day.daily_tasks == "cleaning":
            employee_per_day.base_employees = 3
        elif employee_per_day.daily_tasks == "inventory":
            employee_per_day.base_employees = 2
        else:
            employee_per_day.base_employees = 0

        new_employee_per_day = {
            "day": employee_per_day.day,
            "daily_tasks": employee_per_day.daily_tasks,
            "base_employees": employee_per_day.base_employees,
            "employees_quantity": None
        }

        connection.execute(
            employees_per_day.insert().values(new_employee_per_day))
        connection.commit()

        created_employee_per_day = connection.execute(employees_per_day.select().where(
            employees_per_day.c.day == employee_per_day.day)).first()

    return created_employee_per_day


@employee_per_day.get("/employees_per_day/{day}", response_model=EmployeesPerDay, tags=["employees_per_day"])
def get_employees_per_day(day: str):
    with engine.connect() as connection:
        result = connection.execute(employees_per_day.select().where(
            employees_per_day.c.day == day)).first()
    if not result:
        return {"error": "Entry not found"}
    return result


@employee_per_day.get("/employees_per_day", response_model=list[EmployeesPerDay], tags=["employees_per_day"])
def get_all_employees_per_day():
    with engine.connect() as connection:
        result = connection.execute(employees_per_day.select()).fetchall()
    return result


@employee_per_day.delete("/employees_per_day/{day}", status_code=status.HTTP_204_NO_CONTENT, tags=["employees_per_day"])
def delete_employees_per_day(day: str):
    with engine.connect() as connection:
        result = connection.execute(employees_per_day.delete().where(
            employees_per_day.c.day == day))
        connection.commit()
    if not result.rowcount:
        return {"error": "Entry not found"}

    return Response(status_code=HTTP_204_NO_CONTENT)


def get_day_of_week(loan_date):
    return loan_date.strftime("%A")


def update_days():
    with engine.connect() as connection:
        loans_list = connection.execute(loans.select()).fetchall()

        days_count = {"Monday": 0, "Tuesday": 0, "Wednesday": 0,
                      "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0}

        for loan in loans_list:
            loan_date = loan[4]
            day_of_week = get_day_of_week(loan_date)

            days_count[day_of_week] += 1

    return days_count


@employee_per_day.put("/employees_per_day/update_all", tags=["employees_per_day"])
def update_all_employees_per_day():
    with engine.connect() as connection:
        list_of_days = connection.execute(
            employees_per_day.select()).fetchall()
        days_count = update_days()
        print(list_of_days)
        print(days_count.keys())
        for dia_para_actualizar in list_of_days:

            dia_actualizar_lista = list(dia_para_actualizar)

            print(dia_actualizar_lista[0])
            if dia_actualizar_lista[0] in days_count.keys():
                if dia_actualizar_lista[1] == "cleaning":
                    dia_actualizar_lista[2] = 3
                elif dia_actualizar_lista[1] == "inventory":
                    dia_actualizar_lista[2] = 2
                else:
                    dia_actualizar_lista[2] = 0

                if dia_actualizar_lista[0] in days_count:
                    prestamos_por_dia = days_count[dia_actualizar_lista[0]]
                    print("Prestamos por día:", prestamos_por_dia)
                    empleados_adicionales = prestamos_por_dia // 150
                    print("Empleados adicionales:", empleados_adicionales)
                    dia_actualizar_lista[3] = (
                        dia_actualizar_lista[2] + empleados_adicionales
                    )
                    print("Tarea:", dia_actualizar_lista[1])
                    print("Empleados base:", dia_actualizar_lista[2])
                    print("Cantidad de empleados:", dia_actualizar_lista[3])

                    connection.execute(employees_per_day.update().values(
                        daily_tasks=dia_actualizar_lista[1],
                        base_employees=dia_actualizar_lista[2],
                        employees_quantity=dia_actualizar_lista[3]
                    ).where(employees_per_day.c.day == dia_actualizar_lista[0]))
                connection.commit()


@employee_per_day.put("/employees_per_day/{day}", tags=["employees_per_day"])
def update_employees_per_day(day: str, employee_per_day: EmployeesPerDay):
    with engine.connect() as connection:
        result = connection.execute(employees_per_day.select().where(
            employees_per_day.c.day == day)).first()
        print("Result:", result)
        print(employee_per_day.daily_tasks)
        if employee_per_day.daily_tasks == "cleaning":
            employee_per_day.base_employees = 3
        elif employee_per_day.daily_tasks == "inventory":
            employee_per_day.base_employees = 2
        else:
            employee_per_day.base_employees = 0

        days_count = update_days()
        print(day)
        print(employee_per_day.base_employees)
        print(result[2])

        if day in days_count:
            prestamos_por_dia = days_count[day]
            print("Prestamos por día:", prestamos_por_dia)
            additional_employees = prestamos_por_dia // 150
            print("Empleados adicionales:", additional_employees)
            employee_per_day.employees_quantity = (
                result[2] + additional_employees
            )
            print("Cantidad de empleados:", employee_per_day.employees_quantity)

            result = connection.execute(employees_per_day.update().values(
                daily_tasks=employee_per_day.daily_tasks,
                base_employees=result[2],
                employees_quantity=employee_per_day.employees_quantity
            ).where(employees_per_day.c.day == day))
            print(connection.execute(employees_per_day.select().where(
                employees_per_day.c.day == day)).first())

        connection.commit()
