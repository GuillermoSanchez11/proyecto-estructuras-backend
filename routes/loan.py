from fastapi import APIRouter

loan = APIRouter()


@loan.get("/loan", tags=["loans"])
def get_loan():
    return {"message": "Hello Loan!"}
