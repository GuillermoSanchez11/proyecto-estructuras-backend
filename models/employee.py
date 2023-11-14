from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta, engine


employees = Table("employees", meta,
                  Column("id", (String(15)), primary_key=True),
                  Column("name", String(255)))

meta.create_all(engine)
