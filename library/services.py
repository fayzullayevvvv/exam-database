from datetime import datetime

from .models import Author, Book, Student, Borrow

from .db import get_session


def create_author(name: str, bio: str = None) -> Author:
    """Yangi muallif yaratish"""
    session = get_session()

    author = Author(name=name, bio=bio)

    session.add(author)
    session.commit()
    session.refresh(author)
    session.close()
    return author


def get_author_by_id(author_id: int) -> Author | None:
    """ID bo'yicha muallifni olish"""
    session = get_session()

    author = session.query(Author).filter(Author.id == author_id).first()
    session.close()
    return author


def get_all_authors() -> list[Author]:
    """Barcha mualliflar ro'yxatini olish"""
    session = get_session()

    authors = session.query(Author).all()
    session.close()
    return authors


def update_author(author_id: int, name: str = None, bio: str = None) -> Author | None:
    """Muallif ma'lumotlarini yangilash"""
    session = get_session()

    author = session.get(Author, author_id)
    if not author:
        session.close()
        return None

    if name is not None:
        author.name = name
    if bio is not None:
        author.bio = bio

    session.commit()
    session.refresh(author)

    session.close()
    return author


def delete_author(author_id: int) -> bool:
    """Muallifni o'chirish (faqat kitoblari bo'lmagan holda)"""
    session = get_session()

    author = session.get(Author, author_id)
    if not author:
        session.close()
        return False

    if author.books:
        session.close()
        return False

    session.delete(author)
    session.commit()

    session.close()
    return True


def create_book(
    title: str, author_id: int, published_year: int, isbn: str = None
) -> Book:
    """Yangi kitob yaratish"""
    session = get_session()

    book = Book(
        title=title, author_id=author_id, published_year=published_year, isbn=isbn
    )

    session.add(book)
    session.commit()
    session.refresh(book)

    session.close()
    return book


def get_book_by_id(book_id: int) -> Book | None:
    """ID bo'yicha kitobni olish"""
    session = get_session()

    book = session.query(Book).filter(Book.id == book_id).first()

    session.close()
    return book


def get_all_books() -> list[Book]:
    """Barcha kitoblar ro'yxatini olish"""
    session = get_session()

    books = session.query(Book).all()

    session.close()
    return books


def search_books_by_title(title: str) -> list[Book]:
    """Kitoblarni sarlavha bo'yicha qidirish (partial match)"""
    session = get_session()

    books = session.query(Book).filter(Book.title.ilike(f"%{title}%")).all()

    session.close()
    return books


def delete_book(book_id: int) -> bool:
    """Kitobni o'chirish"""
    session = get_session()

    book = session.get(Book, book_id)
    if not book:
        session.close()
        return False

    session.delete(book)
    session.commit()

    session.close()
    return True


def create_student(full_name: str, email: str, grade: str = None) -> Student:
    """Yangi talaba ro'yxatdan o'tkazish"""
    session = get_session()

    student = Student(full_name=full_name, email=email, grade=grade)

    session.add(student)
    session.commit()
    session.refresh(student)

    session.close()
    return student


def get_student_by_id(student_id: int) -> Student | None:
    """ID bo'yicha talabani olish"""
    session = get_session()

    student = session.query(Student).filter(Student.id == student_id).first()

    session.close()
    return student


def get_all_students() -> list[Student]:
    """Barcha talabalar ro'yxatini olish"""
    session = get_session()

    students = session.query(Student).all()

    session.close()
    return students


def update_student_grade(student_id: int, grade: str) -> Student | None:
    """Talaba sinfini yangilash"""
    session = get_session()

    student = session.get(Student, student_id)

    if not student:
        session.close()
        return None

    student.grade = grade

    session.commit()
    session.refresh(student)

    session.close()
    return student


def borrow_book(student_id: int, book_id: int) -> Borrow | None:
    """
    Talabaga kitob berish

    Quyidagilarni tekshirish kerak:
    1. Student va Book mavjudligini
    2. Kitobning is_available=True ekanligini
    3. Talabada 3 tadan ortiq qaytarilmagan kitob yo'qligini yani 3 tagacha kitob borrow qila oladi

    Transaction ichida:
    - Borrow yozuvi yaratish
    - Book.is_available = False qilish
    - due_date ni hisoblash (14 kun)

    Returns:
        Borrow object yoki None (xatolik bo'lsa)
    """
    session = get_session()

    student = session.get(Student, student_id)
    book = session.get(Book, book_id)

    if not student or not book:
        session.close()
        return None

    if not book.is_available:
        session.close()
        return None

    borrowed_books = (
        session.query(Borrow)
        .filter(Borrow.student_id == student_id)
        .filter(Borrow.returned_at.is_(None))
        .all()
    )

    if len(borrowed_books) >= 3:
        session.close()
        return None

    borrow = Borrow(student_id=student_id, book_id=book_id)
    book.is_available = False

    session.add(borrow)
    session.commit()
    session.refresh(borrow)

    _ = borrow.book
    _ = borrow.student

    session.close()
    return borrow


def return_book(borrow_id: int) -> bool:
    """
    Kitobni qaytarish

    Transaction ichida:
    - Borrow.returned_at ni to'ldirish
    - Book.is_available = True qilish

    Returns:
        True (muvaffaqiyatli) yoki False (xatolik)
    """
    session = get_session()

    borrow = session.query(Borrow).filter(Borrow.id == borrow_id).first()

    if not borrow:
        session.close()
        return False

    if borrow.returned_at:
        session.close()
        raise ValueError("book already returned.")

    borrow.returned_at = datetime.now()
    borrow.book.is_available = True

    session.commit()

    session.close()
    return True


def get_student_borrow_count(student_id: int) -> int:
    """Talabaning jami olgan kitoblari soni"""
    session = get_session()

    count = (
        session.query(Borrow)
        .filter(Borrow.student_id == student_id)
        .filter(Borrow.returned_at.is_(None))
        .count()
    )

    session.close()
    return count


def get_currently_borrowed_books() -> list[tuple[Book, Student, datetime]]:
    """Hozirda band bo'lgan kitoblar va ularni olgan talabalar"""
    session = get_session()

    borrow_records = session.query(Borrow).filter(Borrow.returned_at.is_(None)).all()

    result = [
        (borrow.book, borrow.student, borrow.borrowed_at) for borrow in borrow_records
    ]

    session.close()
    return result


def get_books_by_author(author_id: int) -> list[Book]:
    """Muayyan muallifning barcha kitoblari"""
    session = get_session()

    author = session.get(Author, author_id)
    if not author:
        session.close()
        return []

    books = author.books()

    session.close()
    return books


def get_overdue_borrows() -> list[tuple[Borrow, Student, Book, int]]:
    """
    Kechikkan kitoblar ro'yxati

    Returns:
        List of tuples: (Borrow, Student, Book, kechikkan_kunlar)
        faqat returned_at=NULL va due_date o'tgan yozuvlar
    """
    session = get_session()
    now = datetime.utcnow()

    overdue_records = (
        session.query(Borrow)
        .filter(Borrow.returned_at.is_(None))
        .filter(Borrow.due_date < now)
        .all()
    )

    result = []
    for borrow in overdue_records:
        student = borrow.student
        book = borrow.book
        days_overdue = (now - borrow.due_date).days
        result.append((borrow, student, book, days_overdue))

    session.close()
    return result
