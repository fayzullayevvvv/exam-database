from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import (
    TIMESTAMP,
    func,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Author(Base, TimestampMixin):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base, TimestampMixin):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("authors.id"))
    published_year: Mapped[int] = mapped_column(Integer)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    author: Mapped["Author"] = relationship(back_populates="books")
    borrows: Mapped[list["Borrow"]] = relationship(back_populates="book")


class Student(Base, TimestampMixin):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    borrows: Mapped[list["Borrow"]] = relationship(back_populates="student")


class Borrow(Base, TimestampMixin):
    __tablename__ = "borrows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"))
    borrowed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    due_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.utcnow() + timedelta(days=14)
    )
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    student: Mapped["Student"] = relationship(back_populates="borrows")
    book: Mapped["Book"] = relationship(back_populates="borrows")
