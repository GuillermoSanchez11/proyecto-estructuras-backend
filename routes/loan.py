from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from config.db import conn
from models.loan import loans
from schemas.loan import Loan, LoanPut
from starlette.status import HTTP_204_NO_CONTENT

loan = APIRouter()


@loan.post("/loan", response_model=Loan, tags=["loans"])
def create_loan(loan: Loan):
    new_loan = {
        "id": loan.id,
        "employee_id": loan.employee_id,
        "user_name": loan.user_name,
        "book": loan.book,
        "loan_date": loan.loan_date,
        "devolution_date": loan.devolution_date,
        "return_date": loan.return_date
    }
    print(new_loan)
    result = conn.execute(loans.insert().values(new_loan))
    conn.commit()
    return conn.execute(loans.select().where(loans.c.id == result.lastrowid)).first()


@loan.get("/loan/{id}", response_model=Loan, tags=["loans"])
def get_loan(id: str):
    result = conn.execute(loans.select().where(loans.c.id == id)).first()
    if not result:
        return {"error": "Loan not found"}
    return {"data": {"id": result[0], "employee_id": result[1], "user_name": result[2], "book": result[3], "loan_date": result[4], "devolution_date": result[5], "return_date": result[6]}}


@loan.get("/loan", response_model=list[Loan], tags=["loans"])
def get_loans():
    result = conn.execute(loans.select()).fetchall()
    result_dicts = [{"id": row[0], "employee_id": row[1], "user_name": row[2], "book": row[3],
                     "loan_date": row[4], "devolution_date": row[5], "return_date": row[6]} for row in result]
    response = {"data": result_dicts}
    return response


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
