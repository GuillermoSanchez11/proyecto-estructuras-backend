from fastapi import FastAPI, APIRouter
from routes.loan import loan
from routes.employee import employee
from routes.book import book
from routes.employees_per_day import employee_per_day
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
router = APIRouter()

app.include_router(loan)
app.include_router(employee)
app.include_router(book)
app.include_router(employee_per_day)

origins = [
    "http://localhost",
    "http://localhost:3000",  # Agrega aquí la URL de tu aplicación cliente
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
