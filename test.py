# test.py
from datetime import datetime, timedelta
from library.services import (
    create_author,
    create_book,
    create_student,
    borrow_book,
    return_book,
    get_student_borrow_count,
    get_currently_borrowed_books,
    get_overdue_borrows,
)

def main():
    print("=== Demo Data Test ===")

    # Muallif yaratish
    author1 = create_author("J.K. Rowling", "Famous fantasy author")
    author2 = create_author("George Orwell", "Dystopian fiction author")
    print(f"Created Authors: {author1.name}, {author2.name}")

    # Kitoblar yaratish
    book1 = create_book("Harry Potter and the Philosopher's Stone", author1.id, 1997)
    book2 = create_book("Harry Potter and the Chamber of Secrets", author1.id, 1998)
    book3 = create_book("1984", author2.id, 1949)
    print(f"Created Books: {book1.title}, {book2.title}, {book3.title}")

    # Talabalar yaratish
    student1 = create_student("Alice Smith", "alice@example.com", "10th")
    student2 = create_student("Bob Johnson", "bob@example.com", "11th")
    print(f"Created Students: {student1.full_name}, {student2.full_name}")

    # Kitob berish
    borrow1 = borrow_book(student1.id, book1.id)
    borrow2 = borrow_book(student1.id, book3.id)
    borrow3 = borrow_book(student2.id, book2.id)
    print(f"{student1.full_name} borrowed: {borrow1.book.title}, {borrow2.book.title}")
    print(f"{student2.full_name} borrowed: {borrow3.book.title}")

    # Talabaning olgan kitoblari soni
    count1 = get_student_borrow_count(student1.id)
    count2 = get_student_borrow_count(student2.id)
    print(f"{student1.full_name} currently has {count1} books borrowed")
    print(f"{student2.full_name} currently has {count2} books borrowed")

    # Hozirda band bo'lgan kitoblar
    borrowed_books = get_currently_borrowed_books()
    print("Currently borrowed books:")
    for book, student, borrowed_at in borrowed_books:
        print(f"- {book.title} borrowed by {student.full_name} at {borrowed_at}")

    # Kitobni qaytarish
    return_book(borrow1.id)
    print(f"{borrow1.book.title} returned by {student1.full_name}")

    # Kechikkan kitoblar (demo uchun borrow2 ni 15 kun oldin berilgan qilib o'zgartirish)
    # Agar kerak bo'lsa borrow2.due_date ni o'zgartirish: borrow2.due_date = datetime.utcnow() - timedelta(days=1)
    overdue = get_overdue_borrows()
    print("Overdue borrows:")
    for borrow, student, book, days_overdue in overdue:
        print(f"- {book.title} borrowed by {student.full_name}, overdue by {days_overdue} days")

if __name__ == "__main__":
    main()