from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, DateTime
from config.db import meta, engine
from datetime import datetime
from models.employee import employees

loans = Table("loans", meta,
              Column("id", String(15), primary_key=True),
              Column("employee_id", String(15), ForeignKey(
                  "employees.id")),
              Column("user_name", String(255)),
              Column("book", String(255)),
              Column("loan_date", DateTime, default=datetime.now),
              Column("devolution_date", DateTime, nullable=True),
              Column("return_date", DateTime, nullable=True)
              )

meta.create_all(engine)
