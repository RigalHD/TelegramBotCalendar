from aiogram.types import FSInputFile
from aiogram.types.input_media_photo import InputMediaPhoto
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from abc import ABC, abstractmethod
from typing import overload
from config import GROUP_ID
import sqlite3
import datetime


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
    def remove_info(name: str) -> None:
        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            cursor.execute(
                """
                DELETE FROM info
                WHERE name = ?
                """,
                (name,)
                )

    @staticmethod
    def get_info() -> dict[str, str]:
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
                admin_level INTEGER,
                join_date DATETIME
                )"""
            )

    @staticmethod   
    def add_admin(admin_id: int, admin_level: int = 0) -> None:
        """
        Добавляет админа в таблицу
        :param admin_id: telegram id админа
        """
        try:
            with sqlite3.connect("db.db") as db:
                db.cursor().execute(
                    "INSERT INTO admins (telegram_id, admin_level, join_date) VALUES (?, ?, ?)",
                    (admin_id, admin_level, datetime.datetime.now())
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

    @staticmethod
    def get_admin_level(user_tg_id: int) -> int:
        """
        Проверяет является ли пользователь админом.
        В случае, если пользователь является админом, то возвращает его уровень.
        Если же пользователь не является админом, то возвращает -1
        :param user_tg_id: telegram id пользователя
        """
        try:
            if AdminDatabase.is_admin(user_tg_id):
                with sqlite3.connect("db.db") as db:
                    return db.cursor().execute(
                        "SELECT admin_level FROM admins WHERE telegram_id =?",
                        (user_tg_id,)
                        ).fetchone()[0]
            return -1
        except Exception as e:
            print(e)
            raise e
        
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


class SchedulerDatabase(Database):
    @overload
    def __init__(self, id: int, description: str, date_time: datetime.datetime) -> None: ...
    @overload
    def __init__(self, id: int, description: str, date_time: tuple) -> None: ...

    def __init__(self, id, description, date_time):
        """
        Если в date_time передан кортеж ("31.12.2000", "12:00"),
        то он будет конвертирован в формат datetime.datetime.
        В случае, если сразу передан объект datetime.datetime,
        то с ним ничего не произойдет
        """
        self._id: int = id
        self._description: str = description
        self._expired: bool = False

        if isinstance(date_time, datetime.datetime):
            self._date_time: datetime.datetime = date_time

        elif isinstance(date_time, tuple) and len(date_time) == 2:
            self._date_time = datetime.datetime.strptime(
                f"{date_time[0]} {date_time[1]}",
                "%d.%m.%Y %H:%M"
            )
        
    @staticmethod
    def renew_table() -> None:
        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                day DATE,
                time TIME,
                expired INTEGER,
                group_id INTEGER
                )"""
            )

    @staticmethod
    def get_schedule() -> tuple:
        """
        Возвращает кортеж всех запланированных и непрошедших встреч
        """
        result = []
        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            SchedulerDatabase.renew_table()
            all_data = cursor.execute("SELECT * FROM schedule WHERE expired = 0").fetchall()
            for data in all_data:
                meeting = SchedulerDatabase(
                    id=data[0],
                    date_time=(data[2], data[3])
                )
                if not meeting.is_expired():
                    data = list(data)
                    data[3] = data[3]
                    result.append(tuple(data))

        return tuple(result)
    
    @staticmethod
    def get_actual_meeting() -> tuple:
        """
        Возвращает кортеж с информацией о следующей 
        предстоящей встрече книжного клуба
        """
        with sqlite3.connect("db.db") as db:
            return db.cursor().execute("SELECT * FROM schedule ORDER BY day DESC").fetchone()

        
    @staticmethod
    def add_meeting(
        data: list | tuple,
        reminder_function,
        ) -> True | False:
        """
        Добавляет новую встречу в таблицу расписаний.
        Возвращает True, если встреча была успешно добавлена,
        иначе - False.

        :param data: данные о встрече
        :param reminder_function: функция, отправляющая напоминание
        """
        try:
            data = list(data)
            data.append(0)
            data.append(GROUP_ID)
            data[2] += ":00"

            with sqlite3.connect("db.db") as db:
                cursor = db.cursor()
                meeting_id = cursor.execute("""
                            INSERT INTO schedule (
                            description,
                            day, 
                            time, 
                            expired,
                            group_id
                            ) VALUES (?, ?, ?, ?, ?) 
                            RETURNING id
                            """,
                            data
                ).fetchone()[0]

                SchedulerDatabase.add_job(
                    data=data,
                    id=meeting_id,
                    reminder_function=reminder_function
                )
                return True
            
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def add_job(
        data: tuple | list,
        id: int,
        reminder_function
        ) -> None:
        """
        Добавляет "работу" через библиотеку apscheduler
        :param data: данные о встрече
        :param id: id встречи в таблице
        :param reminder_function: функция, отправляющая напоминание
        """
        hour, minute = data[2].split(":")
        new_job_id = "scheduler_job_" + str(id)
                
        info_message = f"""Внимание! Напоминаем о встрече книжного клуба!
        Что на ней будет? - <b>{data[0]}</b>
        Когда она будет? - <b>{hour}:{minute}</b>
        Во сколько приходить? - <b>{data[1]}</b> """

        day, month, year = data[1].replace(",", ".").split(".")
        date = datetime.datetime.strptime(f'{year}-{month}-{day}', "%Y-%m-%d") + datetime.timedelta(days=1)
        scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
        scheduler.add_job(
            reminder_function,
            'cron',
            hour=12,
            minute=00,
            day_of_week="sat",
            start_date=datetime.datetime.now(),
            end_date=date,
            kwargs={
                "info_message": info_message,
                "group_id": GROUP_ID
            },
            id=new_job_id
        )

        scheduler.start()

    def is_expired(self) -> True | False:
        """
        Устанавливает статус встречи как просроченную,
        если она является таковой и возращает True,
        если же встреча не просрочена, то возвращает False
        """
        if self._expired:
            return True
        if datetime.datetime.now() > self._date_time:
            with sqlite3.connect("db.db") as db:
                db.cursor().execute(
                    "UPDATE schedule SET expired = 1 WHERE id = ?",
                    (self._id,)
                )
            self._expired = True
            return True
        return False


    @property
    def id(self) -> int:
        return self._id


class BookDatabase(Database):
    def __init__(self, id: int):
        self._id: int = id
        self.BOOKS_COLUMNS_RUS_NAMES: tuple = (
            "Название", "Описание", "Автор", "Жанр",
            "Год", "Экранизации", "Рейтинг", "Возраcт"
            )
        self.FULL_BOOKS_COLUMNS_RUS_NAMES: tuple = (
            "ID", "Название", "Описание", "Автор", "Жанр",
            "Год", "Экранизации", "Рейтинг", "Возраcт", "Обложка"
            )
        
    @staticmethod
    def remove_book_by_id(id: int) -> None:
        """
        Удаляет книгу по ее айди
        :param id: id книги в таблице
        """
        try:
            with sqlite3.connect("db.db") as db:
                db.cursor().execute("DELETE FROM books WHERE id = ?", (id,))
        except Exception as e:
            print(e)

    
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
    def renew_table() -> None:
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
                    film_adaptations TEXT,
                    rating REAL,
                    age_rating CHAR,
                    image BLOB DEFAULT NULL
                    )""")

    def get_columns_names_dict(
            self,
            full: bool = False
            ) -> dict | None:
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
    