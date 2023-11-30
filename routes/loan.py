from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from config.db import conn, engine
from models.employees_per_day import employees_per_day
from models.book import books
from models.loan import loans
from models.employee import employees
from schemas.loan import Loan, LoanPut, LoanReturn
from schemas.employee import Employee
from schemas.book import Book
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, select, text, update
from typing import List
from pydantic import BaseModel


class LoansResponse(BaseModel):
    employees: List[Employee]
    books: List[Book]


loan = APIRouter()


@loan.post("/loan", response_model=Loan, tags=["loans"])
def create_loan(loan: Loan):

    with engine.connect() as connection:
        loan_date = loan.loan_date
        week_day = loan_date.strftime("%A")
        new_loan = {
            "id": loan.id,
            "employee_id": loan.employee_id,
            "user_name": loan.user_name,
            "book_id": loan.book_id,
            "loan_date": loan_date,
            "devolution_date": loan.devolution_date,
            "return_date": None,
            "week_day": week_day
        }
        connection.execute(loans.insert().values(new_loan))
        loan_created = connection.execute(
            loans.select().where(loans.c.id == loan.id)).first()
        connection.commit()

    return loan_created


@loan.get("/loan/return", response_model=list[Loan], tags=["loans"])
def get_loan_by_return_date():
    with engine.connect() as connection:
        result = connection.execute(
            loans.select().where(loans.c.return_date == None))

    return result


@loan.get("/loan/{id}", response_model=Loan, tags=["loans"])
def get_loan(id: str):
    with engine.connect() as connection:
        result = connection.execute(
            loans.select().where(loans.c.id == id)).first()

    if not result:
        return JSONResponse(status_code=404, content={"detail": "Loan not found"})
    return result


@loan.get("/loan", response_model=list[Loan], tags=["loans"])
def get_loans():
    with engine.connect() as connection:
        result = connection.execute(loans.select()).fetchall()
    return result


@loan.delete("/loan/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["loans"])
def delete_loan(id: str):
    with engine.connect() as connection:
        result = connection.execute(loans.delete().where(loans.c.id == id))

    if not result.rowcount:
        return {"error": "Loan not found"}
    connection.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)


@loan.put("/loan/{id}", response_model=LoanPut, tags=["loans"])
def update_loan(id: str, loan: LoanPut):
    with engine.connect() as connection:
        result = connection.execute(loans.update().values(
            devolution_date=loan.devolution_date,
            return_date=loan.return_date
        ).where(loans.c.id == id))
        connection.commit()
        loan_updated = connection.execute(
            loans.select().where(loans.c.id == id)).first()

    if not result.rowcount:
        return JSONResponse(status_code=404, content={"detail": "Loan not found"})

    return loan_updated


@loan.put("/loan/{id}/return", response_model=LoanPut, tags=["loans"])
def return_loan(id: str, loan: Loan):
    with engine.connect() as connection:
        result = connection.execute(loans.update().values(
            return_date=loan.return_date
        ).where(loans.c.id == id))
        result_date = connection.execute(
            loans.select().where(loans.c.id == id)).first()
        print("result date:", result_date)

        book_id = connection.execute(
            loans.select().where(loans.c.id == id)).first()[3]

        consulta = text(
            f"SELECT COUNT(*) FROM loans WHERE book_id = {book_id}")
        count = connection.execute(consulta).scalar()
        print("Count:", count)

        loans_with_same_book_id = connection.execute(
            select(loans).where(loans.c.book_id == book_id)).fetchall()

        print("loans_with_same_book_id:", loans_with_same_book_id)

        total_difference = 0
        for loan_row in loans_with_same_book_id:
            total_difference += (loan_row.return_date -
                                 loan_row.devolution_date).days

        count = len(loans_with_same_book_id)
        average_difference = total_difference / count
        suggestion = round(average_difference, 2)
        print("Suggestion:", suggestion)

        update_statement = update(books).values(Suggestion=suggestion).where(
            books.c.book_id == book_id)
        connection.execute(update_statement)

        difference = result_date[6] - result_date[5]

        print("Difference:", difference)
        connection.commit()
        retornar = connection.execute(
            loans.select().where(loans.c.id == id)).first()

    if not result.rowcount:
        return JSONResponse(status_code=404, content={"detail": "Loan not found"})
    return retornar


@loan.post("/loan/update_suggestions", response_model=None, tags=["loans"])
def update_suggestions():
    with engine.connect() as connection:
        loans_list = connection.execute(loans.select()).fetchall()
        for loan in loans_list:
            book_id = loan[3]
            consulta = text(
                f"SELECT COUNT(*) FROM loans WHERE book_id = {book_id}")
            count = connection.execute(consulta).scalar()

            loans_with_same_book_id = connection.execute(
                select(loans).where(loans.c.book_id == book_id)).fetchall()

            total_difference = 0
            for loan_row in loans_with_same_book_id:
                total_difference += (loan_row.return_date -
                                     loan_row.devolution_date).days

            count = len(loans_with_same_book_id)
            average_difference = total_difference / count
            suggestion = round(average_difference, 2)

            update_statement = update(books).values(Suggestion=suggestion).where(
                books.c.book_id == book_id)
            connection.execute(update_statement)

        connection.commit()


def get_day_of_week(loan_date):
    return loan_date.strftime("%A")


@loan.post("/loan/update_days", response_model=None, tags=["loans"])
def update_days():
    with engine.connect() as connection:
        loans_list = connection.execute(loans.select()).fetchall()

        days_count = {"Monday": 0, "Tuesday": 0, "Wednesday": 0,
                      "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0}

        for loan in loans_list:
            loan_date = loan[4]
            day_of_week = get_day_of_week(loan_date)

            update_statement = update(loans).values(
                week_day=day_of_week).where(loans.c.id == loan[0])
            connection.execute(update_statement)

            days_count[day_of_week] += 1

        connection.commit()
        print("Days count:", days_count)

    return days_count


@loan.post("/loan/update_days_limited", response_model=None, tags=["loans"])
def update_days_limited():
    with engine.connect() as connection:
        query = select(loans).limit(1000)

        loans_list = connection.execute(query).fetchall()

        days_count = {"Monday": 0, "Tuesday": 0, "Wednesday": 0,
                      "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0}

        for loan in loans_list:
            loan_date = loan[4]
            day_of_week = get_day_of_week(loan_date)

            update_statement = update(loans).values(
                week_day=day_of_week).where(loans.c.id == loan[0])
            connection.execute(update_statement)

            days_count[day_of_week] += 1

        connection.commit()
        print("Days count:", days_count)

    return {"message": "Days updated and counted"}
