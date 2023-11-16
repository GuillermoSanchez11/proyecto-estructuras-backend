from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, DateTime
from config.db import meta, engine
from datetime import datetime

loans = Table("loans", meta,
              Column("id", String, primary_key=True),
              Column("employee_id", String, ForeignKey("employees.id")),
              Column("user_name", String(255)),
              Column("book", String(255)),
              Column("loan_date", DateTime, default=datetime.now),
              Column("devolution_date", DateTime, nullable=True),
              Column("return_date", DateTime, nullable=True)
              )

meta.create_all(engine)
