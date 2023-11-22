from fastapi import FastAPI, APIRouter
from routes.loan import loan
from routes.employee import employee
from routes.book import book


app = FastAPI()
router = APIRouter()

app.include_router(loan)
app.include_router(employee)
app.include_router(book)
