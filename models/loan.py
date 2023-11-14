from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, DateTime
from config.db import meta, engine
from datetime import datetime

loans = Table("loans", meta,
              Column("id", Integer, primary_key=True),
              Column("employee_name", String(255)),
              Column("user_name", String(255)),
              Column("book", String(255)),
              Column("loan_date", DateTime, default=datetime.now),
              Column("return_date", DateTime, nullable=True)
              )

meta.create_all(engine)
