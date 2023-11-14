from fastapi import APIRouter

loan = APIRouter()


@loan.get("/loan")
def hello_loan():
    return {"message": "Hello Loan!"}
