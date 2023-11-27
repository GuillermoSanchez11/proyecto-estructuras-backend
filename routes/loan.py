from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from config.db import conn
from models.employees_per_day import employees_per_day
from models.book import books
from models.loan import loans
from schemas.loan import Loan, LoanPut, LoanReturn
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, select, text, update

loan = APIRouter()

Session = sessionmaker(bind=conn)
session = Session()


@loan.post("/loan", response_model=Loan, tags=["loans"])
def create_loan(loan: Loan):

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

    conn.execute(loans.insert().values(new_loan))
    conn.commit()

    return conn.execute(loans.select().where(loans.c.id == loan.id)).first()


@loan.get("/loan/{id}", response_model=Loan, tags=["loans"])
def get_loan(id: str):
    result = conn.execute(loans.select().where(loans.c.id == id)).first()
    if not result:
        return {"error": "Loan not found"}
    return {"data": {"id": result[0], "employee_id": result[1], "user_name": result[2], "book_id": result[3], "loan_date": result[4], "devolution_date": result[5], "return_date": result[6]}}


@loan.get("/loan", response_model=list[Loan], tags=["loans"])
def get_loans():
    result = conn.execute(loans.select()).fetchall()
    return result


@loan.delete("/loan/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["loans"])
def delete_loan(id: str):
    result = conn.execute(loans.delete().where(loans.c.id == id))
    if not result.rowcount:
        return {"error": "Loan not found"}
    conn.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)


@loan.put("/loan/{id}", response_model=LoanPut, tags=["loans"])
def update_loan(id: str, loan: LoanPut):
    result = conn.execute(loans.update().values(
        devolution_date=loan.devolution_date,
        return_date=loan.return_date
    ).where(loans.c.id == id))
    if not result.rowcount:
        return JSONResponse(status_code=404, content={"detail": "Loan not found"})
    conn.commit()
    return conn.execute(loans.select().where(loans.c.id == id)).first()


@loan.put("/loan/{id}/return", response_model=Loan, tags=["loans"])
def return_loan(id: str, loan: Loan):
    result = conn.execute(loans.update().values(
        return_date=loan.return_date
    ).where(loans.c.id == id))
    result_date = conn.execute(loans.select().where(loans.c.id == id)).first()
    print("result date:", result_date)

    book_id = conn.execute(loans.select().where(loans.c.id == id)).first()[3]

    consulta = text(f"SELECT COUNT(*) FROM loans WHERE book_id = {book_id}")
    count = conn.execute(consulta).scalar()
    print("Count:", count)

    loans_with_same_book_id = conn.execute(
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
    conn.execute(update_statement)

    difference = result_date[6] - result_date[5]

    print("Difference:", difference)
    if not result.rowcount:
        return JSONResponse(status_code=404, content={"detail": "Loan not found"})
    conn.commit()
    return conn.execute(loans.select().where(loans.c.id == id)).first()


@loan.post("/loan/update_suggestions", response_model=None, tags=["loans"])
def update_suggestions():
    loans_list = conn.execute(loans.select()).fetchall()
    for loan in loans_list:
        book_id = loan[3]
        consulta = text(
            f"SELECT COUNT(*) FROM loans WHERE book_id = {book_id}")
        count = conn.execute(consulta).scalar()

        loans_with_same_book_id = conn.execute(
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
        conn.execute(update_statement)

    conn.commit()


def get_day_of_week(loan_date):
    return loan_date.strftime("%A")


@loan.post("/loan/update_days", response_model=None, tags=["loans"])
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


@loan.post("/loan/update_days_limited", response_model=None, tags=["loans"])
def update_days_limited():

    query = select(loans).limit(1000)

    loans_list = conn.execute(query).fetchall()

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

    return {"message": "Days updated and counted"}
