from aiogram.types import FSInputFile
from aiogram.types.input_media_photo import InputMediaPhoto
import sqlite3


class Database:
    def __init__(self):
        pass

    def get_colunms_names(self, table_name: str) -> tuple | None:
        """
        Возвращает кортеж названий колонок таблицы
        или None, если возникла ошибка или таблица не существует
        """
        with sqlite3.connect("db.db") as db:
            try:
                result = [
                    column[1] for column in db.cursor().execute(
                        f"PRAGMA table_info({table_name})").fetchall()
                        ]
                return result if result else None
            except Exception as e:
                print(e)
                return None


class BookDatabase(Database):
    def __init__(self, id: int):
        self._id: int = id
        self.BOOKS_COLUMNS_RUS_NAMES: tuple = (
            "Название", "Описание", "Автор", "Жанр",
            "Год", "Издательство", "Рейтинг", "Возраcт"
            )
        self.FULL_BOOKS_COLUMNS_RUS_NAMES: tuple = (
            "ID", "Название", "Описание", "Автор", "Жанр",
            "Год", "Издательство", "Рейтинг", "Возраcт", "Обложка"
            )
    
    @staticmethod
    def get_colunms_names(full: bool = False) -> list | None:
        """
        Возвращает все колонки таблицы книг
        :param full: True - возвращает все колонки таблицы, False - возвращает все колонки, кроме айди и обложки
        """
        try:
            with sqlite3.connect("db.db") as db:
                cursor = db.cursor()
                books_columns = [
                    column[1] for column in cursor.execute(
                        "PRAGMA table_info(books)").fetchall()
                        ]
                if not full:
                    # Удаляет id и image из названий колонок
                    books_columns = books_columns[1:-1]
                
                return books_columns if books_columns else None
        except Exception as e:
            print(e)
            return None
    
    @staticmethod
    def get_all_books_info() -> tuple:
        """
        Возвращает кортеж всех книг
        """
        with sqlite3.connect("db.db") as db:
            try:
                result = db.cursor().execute(
                    "SELECT * FROM books"
                    ).fetchall()
                return result if result else None
            except Exception as e:
                print(e)
                return None
    
    @staticmethod
    def get_all_books() -> dict:
        """
        Возвращает словарь всех книг
            {
            айди: {
            "колонка": "информация",
            "колонка2": "информация2",
                },
            айди2: {
            "колонка": "информация",
            "колонка2": "информация2",
            }, ...
            }
        или возвращает None, если возникла ошибка или книг нет
        """
        try:
            books_dict = {}
            all_books = BookDatabase.get_all_books_info()
            books_keys = BookDatabase.get_colunms_names(full=True)
            # print(books_keys)
            for book in all_books:
                books_dict[book[0]] = {}
                for key, value in zip(books_keys[1:], book[1:]):
                    books_dict[book[0]][key] = value
            return books_dict if books_dict else None
        except Exception as e:
            print(e)
            return None


    
    def get_columns_names_dict(self, full: bool = False) -> dict | None:
        """
        Возвращает словарь c колонками таблицы книг ("Имя колонки на русском": "Имя колонки в таблице")
        или возвращает None, если возникла ошибка
        """
        try:
            if full:
                return dict(zip(
                    self.FULL_BOOKS_COLUMNS_RUS_NAMES,
                    self.get_colunms_names(full=full),
                ))
            else:
                return dict(zip(
                    self.BOOKS_COLUMNS_RUS_NAMES,
                    self.get_colunms_names(full=full),
                ))
        except Exception as e:
            print(e)
            return None

    def get_full_book_info(self, full: bool = False) -> dict | None:
        """
        Возвращает словарь c информацией ("Имя колонки в таблицу": "информация")
        о книге или возвращает None, если возникла ошибка или книга не существует
        """
        try:
            with sqlite3.connect("db.db") as conn:
                cursor = conn.cursor()
                book_info = cursor.execute("""
                                    SELECT *
                                    FROM books WHERE id = ?
                                    """,
                                    (self._id,)
                                    ).fetchone()

            if full:
                return dict(zip(
                    self.get_colunms_names(full=full),
                    book_info
                ))
            else:
                return dict(zip(
                    self.get_colunms_names(full=full),
                    book_info[1:-1]
                ))                   
                
        except Exception as e:
            print(e)
            return None
    
    def get_book_info(self, column_name: str) -> str | None:
        """
        Возвращает информацию об определенном "свойстве" книги 
        (например, описание, или название, или автор)
        :param column_name: название "свойства" (Название колонки в таблице)
        """
        try:
            with sqlite3.connect("db.db") as db:
                return str(db.cursor().execute(f""" 
                            SELECT {column_name}
                            FROM books WHERE id = ?
                            """, (self._id,)
                            ).fetchone()[0])
        except Exception as e:
            print("!!!" + str(e))
            return None

    def get_book_photo_path(self) -> str | None:
        """Возвращает путь к обложке книги"""
        try:
            with sqlite3.connect("db.db") as db:
                book_photo_path = db.cursor().execute(
                    "SELECT image FROM books WHERE id = ?",
                    (self._id,)
                    ).fetchone()
                return book_photo_path[0] if book_photo_path else None
            
        except Exception as e:
            print(e)
            return None
        
    def get_book_photo(
            self,
            FSINPUTFILE: bool = True
            ) -> FSInputFile | InputMediaPhoto | None:
        """
        Возвращает обложку книги
        или None, если возникла ошибка или книга не существует
        :param FSINPUTFILE: True - FSInputFile, False - InputMediaPhoto
        """
        try:
            book_photo_file = FSInputFile(self.get_book_photo_path())
            return book_photo_file\
                if FSINPUTFILE else InputMediaPhoto(media=book_photo_file)
        
        except Exception as e:
            print(e)
            return None
    
    @property
    def id(self) -> int:
        return self._id
    