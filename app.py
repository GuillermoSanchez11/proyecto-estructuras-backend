from fastapi import FastAPI, APIRouter
from routes.loan import loan
from routes.employee import employee
from config.db import conn
from models.employee import employees


app = FastAPI()
router = APIRouter()

app.include_router(loan)
app.include_router(employee)
