from sqlalchemy import Table, Column
from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import String, Integer
from config.db import meta, engine

books = Table(
    "books", meta,
    Column("book_id", String(15), primary_key=True),
    Column("title", String(255)),
    Column("author", String(255)),
    Column("genre", String(50)),
    Column("year", String(4)),
    Column("Suggestion", Integer, nullable=True)
)

meta.create_all(engine)
