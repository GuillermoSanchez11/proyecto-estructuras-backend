from fastapi import APIRouter, Response, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.db import conn, engine
from models.book import books
from schemas.book import Book
from sqlalchemy import func

book = APIRouter()


@book.post("/book", response_model=Book, tags=["books"])
def create_book(book: Book):
    with engine.connect() as connection:
        new_book = {
            "book_id": book.book_id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "year": book.year,
        }
        connection.execute(books.insert().values(new_book))
        connection.commit()
        book_created = connection.execute(books.select().where(
            books.c.book_id == book.book_id)).first()
    return book_created


@book.get("/book/{book_id}", response_model=Book, tags=["books"])
def get_book(book_id: str):
    with engine.connect() as connection:
        result = connection.execute(books.select().where(
            books.c.book_id == book_id)).first()
    if not result:
        raise HTTPException(status_code=404, detail="Book not found")
    return result


@book.get("/book", response_model=list[Book], tags=["books"])
def get_books():
    with engine.connect() as connection:
        result = connection.execute(books.select()).fetchall()
    return result


@book.delete("/book/{book_id}", tags=["books"])
def delete_book(book_id: str):
    with engine.connect() as connection:
        result = connection.execute(books.delete().where(books.c.book_id == book_id))
        if not result.rowcount:
            raise HTTPException(status_code=404, detail="Book not found")
        connection.commit()
    return {"message": "Book deleted successfully"}


@book.put("/book/{book_id}", response_model=Book, tags=["books"])
def update_book(book_id: str, book: Book):
    with engine.connect() as connection:
        result = connection.execute(books.update().values(
            title=book.title,
            author=book.author,
            genre=book.genre,
            year=book.year
        ).where(books.c.book_id == book_id))
        if not result.rowcount:
            return JSONResponse(status_code=404, content={
                "detail": "Book not found"})
        connection.commit()
        book_updated = connection.execute(books.select().where(
            books.c.book_id == book_id)).first()
    return book_updated
