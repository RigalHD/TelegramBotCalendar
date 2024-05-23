from aiogram.types import FSInputFile
from aiogram.types.input_media_photo import InputMediaPhoto
# from abc import ABC, abstractmethod
import sqlite3
import datetime
from typing import Dict

class Database:
    def __init__(self):
        pass
    
    def renew_table(self):
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


class InfoDatabase(Database):
    @staticmethod
    def renew_table():
        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS info(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                last_changed DATETIME NOT NULL
                )"""
                )

    @staticmethod
    def add_info(name: str, description: str) -> None:
        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            cursor.execute(
                """
                INSERT INTO info(name, description, last_changed)
                VALUES(?, ?, ?)
                """,
                (name, description, datetime.datetime.now())
                )
    
    @staticmethod
    def update_info(name: str, description: str) -> None:
        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            cursor.execute(
                """
                UPDATE info SET description = ?, last_changed = ?
                WHERE name = ?
                """,
                (description, datetime.datetime.now(), name)
                )

    @staticmethod
    def get_info() -> Dict[str, str]:
        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            result = cursor.execute(
                """
                SELECT name, description FROM info
                """
                ).fetchall()
            return {column[0]: column[1] for column in result}
                


class AdminDatabase(Database):
    @staticmethod
    def renew_table():
        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS admins(
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER NOT NULL,
                join_date DATETIME
                )"""
                )

    @staticmethod   
    def add_admin(admin_id: int) -> None:
        """
        Добавляет админа в таблицу
        :param admin_id: telegram id админа
        """
        try:
            with sqlite3.connect("db.db") as db:
                db.cursor().execute(
                    "INSERT INTO admins (telegram_id, join_date) VALUES (?, ?)",
                    (admin_id, datetime.datetime.now())
                )
        except Exception as e:
            print(e)
            raise e

    @staticmethod
    def is_admin(user_tg_id: int) -> bool:
        """
        Проверяет является ли пользователь админом
        :param user_tg_id: telegram id пользователя
        :return: True - админ, False - нет
        """
        try:
            with sqlite3.connect("db.db") as db:
                result = bool(db.cursor().execute(
                    "SELECT EXISTS(SELECT 1 FROM admins WHERE telegram_id = ?)",
                    (user_tg_id,)
                ).fetchone()[0])
                return result
        except Exception as e:
            print(e)
            raise e

    # @staticmethod
    # def remove_admin(admin_id: int) -> None:
    #     """
    #     Удаляет админа из таблицы по внутреннему айди таблицы
    #     :param admin_id: telegram id админа
    #     """
    #     with sqlite3.connect("db.db") as db:
    #         try:
    #             db.cursor().execute(
    #                 "DELETE FROM admins WHERE id = ?",
    #                 admin_id
    #             )
    #         except Exception as e:
    #             print(e)

    @staticmethod
    def remove_admin(admin_tg_id: int) -> None:
        """
        Удаляет админа из таблицы по его telegram айди
        :param admin_id: telegram id админа
        """
        with sqlite3.connect("db.db") as db:
            try:
                db.cursor().execute(
                    "DELETE FROM admins WHERE telegram_id = ?",
                    (admin_tg_id,)
                )
            except Exception as e:
                print(e)


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
        
    
    @staticmethod
    def get_amount_of_books(amount: int) -> dict:
        """
        Возвращает словарь последних книг (по количеству, указанному в параметре amout)
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
            all_books = BookDatabase.get_all_books_info()[-abs(amount):]
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

    @staticmethod
    def create_if_not_exists() -> None:
        """
        Создает таблицу книг, если таковой не было
        """
        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    author CHAR,
                    genre CHAR,
                    year INTEGER,
                    publishing_house CHAR,
                    rating REAL,
                    age_rating CHAR,
                    image BLOB DEFAULT NULL
                    )""")

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

    def get_full_book_info(
            self,
            has_id: bool = False,
            has_name: bool = True,
            has_description: bool = True,
            has_image: bool = False,
            has_rus_copolumns: bool = False,
           ) -> dict | None:
        """
        Возвращает словарь c информацией ("Имя колонки в таблицу": "информация")
        о книге или возвращает None, если возникла ошибка или книга не существует

        :param has_id: True - итог без изменений, False - айди книги не будет в итоговом словаре
        :param has_name: True - итог без изменений, False - название книги не будет в итоговом словаре
        :param has_description: True - итог без изменений, False - описание книги не будет в итоговом словаре
        :param has_image: True - итог без изменений, False - обложка книги не будет в итоговом словаре
        :param has_rus_copolumns: True - имена колонок будут на русском языке, False - имена колонок будут на английском языке

        """
        try:
            with sqlite3.connect("db.db") as db:
                cursor = db.cursor()
                book_info = list(cursor.execute("""
                    SELECT *
                    FROM books WHERE id = ?
                    """,
                    (self._id,)
                ).fetchone())
            result = dict(zip(
                    self.get_colunms_names(full=True),
                    book_info
                ))

            if not has_id:
                result.pop("id")
            if not has_name:
                result.pop("name")
            if not has_description:
                result.pop("description")
            if not has_image:
                result.pop("image")
            if result["rating"] is None: # У книги может быть еще не определен рейтинг
                result.pop("rating")
            if has_rus_copolumns:
                for el in self.get_columns_names_dict(full=True).items():
                    if el[1] in result:
                        result[el[0]] = result[el[1]]
                        result.pop(el[1])
            return result
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
    