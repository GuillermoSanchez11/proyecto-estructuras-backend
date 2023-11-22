from fastapi import APIRouter, Response, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.db import conn
from models.book import books
from schemas.book import Book
from sqlalchemy import func

book = APIRouter()


@book.post("/book", response_model=Book, tags=["books"])
def create_book(book: Book):
    new_book = {
        "book_id": book.book_id,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "year": book.year,
    }
    result = conn.execute(books.insert().values(new_book))
    conn.commit()
    return conn.execute(books.select().where(books.c.book_id == book.book_id)).first()


@book.get("/book/{book_id}", response_model=Book, tags=["books"])
def get_book(book_id: str):
    result = conn.execute(books.select().where(
        books.c.book_id == book_id)).first()
    if not result:
        raise HTTPException(status_code=404, detail="Book not found")
    return result


@book.get("/book", response_model=list[Book], tags=["books"])
def get_books():
    result = conn.execute(books.select()).fetchall()

    return result


@book.delete("/book/{book_id}", tags=["books"])
def delete_book(book_id: str):
    result = conn.execute(books.delete().where(books.c.book_id == book_id))
    if not result.rowcount:
        raise HTTPException(status_code=404, detail="Book not found")
    conn.commit()
    return {"message": "Book deleted successfully"}


@book.put("/book/{book_id}", response_model=Book, tags=["books"])
def update_book(book_id: str, book: Book):
    result = conn.execute(books.update().values(
        title=book.title,
        author=book.author,
        genre=book.genre,
        year=book.year
    ).where(books.c.book_id == book_id))
    if not result.rowcount:
        return JSONResponse(status_code=404, content={
            "detail": "Book not found"})
    conn.commit()
    return conn.execute(books.select().where(books.c.book_id == book_id)).first()
