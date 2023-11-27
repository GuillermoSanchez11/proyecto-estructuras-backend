from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import String, Integer
from config.db import meta, engine

employees_per_day = Table("employees_per_day", meta,
                          Column("day", (String(15)), primary_key=True),
                          Column("daily_tasks", String(1000)),
                          Column("base_employees", Integer),
                          Column("employees_quantity", Integer, nullable=True)
                          )
meta.create_all(engine)
