from fastapi import FastAPI
from routes.loan import loan
from routes.employee import employee

app = FastAPI()

app.include_router(loan)
app.include_router(employee)
