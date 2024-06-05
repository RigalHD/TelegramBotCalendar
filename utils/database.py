from aiogram.types import FSInputFile
from aiogram.types.input_media_photo import InputMediaPhoto
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from abc import ABC, abstractmethod
from typing import Union
from config import GROUP_ID
import sqlite3
import datetime


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


class ProfilesDatabase(Database):
    def __init__(self, telegram_id: int):
        self._all_data: dict[str: Union[int, str, None, datetime.date]] = \
            ProfilesDatabase.get_profile_info(telegram_id)
        self._id: int = self._all_data["id"]
        self._telegram_id: int = self._all_data["telegram_id"]
        self._name: str = self._all_data["name"]
        self._bio: str = self._all_data["bio"]
        self._favorite_books_ids: list = self._all_data["favorite_books_ids"]
        self._join_date: datetime.date = self._all_data["join_date"]

    @staticmethod
    def renew_table() -> None:
        with sqlite3.connect("db.db") as db:
            db.cursor().execute("""CREATE TABLE IF NOT EXISTS profiles(
                                id INTEGER PRIMARY KEY, 
                                telegram_id INTEGER NOT NULL UNIQUE,
                                name TEXT DEFAULT NULL,
                                bio TEXT DEFAULT 'Описание отсутствует',
                                favorite_books TEXT,
                                join_date DATE NOT NULL
                                )"""
                                )

    @staticmethod
    def get_profile_info(
        telegram_id: int
        ) -> dict[str: Union[int, str, None, datetime.date]]:
        """
        Возвращает словарь, в котором находятся все данные о пользователе
        
        :param telegram_id: telegram id пользователя
        """
        if not ProfilesDatabase.does_profile_exist(telegram_id):
            ProfilesDatabase.add_profile(telegram_id)

        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            data = list(cursor.execute(
                """SELECT *
                FROM profiles
                WHERE telegram_id = ?""",
                (telegram_id,)
            ).fetchone())
            data[4] = [] if data[4] in ("  ", " ", "") else data[4]
            # print(f"!{data[4]}!")
            return {
                "id": int(data[0]),
                "telegram_id": data[1],
                "name": data[2],
                "bio": data[3],
                "favorite_books_ids": [int(book_id) for book_id in data[4][1:-1].split("  ")] if data[4] else [],
                "join_date": datetime.datetime.strptime(data[5], "%Y-%m-%d").date().strftime("%d.%m.%Y")
            }
    
    @staticmethod
    def does_profile_exist(telegram_id: int) -> bool:
        """
        :param telegram_id: telegram id пользователя
        :return: True - профиль пользователя существует, False - нет
        """
        ProfilesDatabase.renew_table()
        with sqlite3.connect("db.db") as db:
            return bool(db.cursor().execute(
                "SELECT COUNT(*) FROM profiles WHERE telegram_id = ?""", 
                (telegram_id,)
                ).fetchone()[0]
            )

    @staticmethod
    def add_profile(telegram_id: int) -> True | False:
        """
        Добавляет новый профиль в таблицу,
        если такого еще нет

        :param telegram_id: telegram id пользователя
        :return: True - успех, False - возникла ошибка, или пользователь уже существует
        """
        try:
            with sqlite3.connect("db.db") as db:
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO profiles(telegram_id, join_date) VALUES(?, ?)",
                    (telegram_id, datetime.datetime.now().date())
                )
        except Exception as e:
            print(e)
            return False

    def add_favorite_book(self, book_id: int) -> True | False:
        """
        Назначает книгу любимой для пользователя.
        В таблице хранятся в таком формате (через пробел):
        айди_книги1 айди_книги2 айди_книги3

        :param book_id: id книги
        :return: True - успех, False - возникла ошибка или книга уже является любимой
        """
        try:
            if int(book_id) in self._favorite_books_ids:
                return False
            with sqlite3.connect("db.db") as db:
                db.cursor().execute("""
                            UPDATE profiles 
                            SET favorite_books = COALESCE(favorite_books, '') || ?  
                            WHERE id = ?""", (" " + str(book_id) + " ", self._id)
                            )
                self._favorite_books_ids.append(int(book_id))
                db.cursor().execute("UPDATE books SET rating = rating + 1 WHERE id = ?", (int(book_id),))
            return True
        except Exception as e:
            print(e)
            return False
        
    def is_book_favorite(self, book_id: int) -> bool:
        """
        Проверяет, находится ли книга в списке любимых книг пользователя

        :param book_id: id книги
        """
        return(bool(int(book_id) in self._favorite_books_ids))
            

    def remove_favorite_book(self, book_id: int) -> True | False:
        """
        Удаляет книгу из списка любимых книг пользователяы

        :param book_id: id книги
        :return True - успех, False - возникла ошибка или книга не является любимой
        """
        try:
            if book_id not in self._favorite_books_ids:
                return False
            with sqlite3.connect("db.db") as db:
                self._favorite_books_ids.remove(int(book_id))
                
                formated_favorite_books_ids = None if not self._favorite_books_ids else \
                    " " + "  ".join([str(book_id) for book_id in self._favorite_books_ids]) + " "
                db.cursor().execute(
                    "UPDATE profiles SET favorite_books = ? WHERE id = ?", 
                    (formated_favorite_books_ids, self._id)
                    )
                db.cursor().execute("UPDATE books SET rating = rating - 1 WHERE id = ?", (int(book_id),))
            return True
        except Exception as e:
            print(e)
            return False

    def change_bio(self, bio: str) -> True | False:
        """
        Изменяет биографию пользователя
        
        :param bio: новая биография пользователя
        :return: True - успех, False - возникла ошибка
        """
        try:
            with sqlite3.connect("db.db") as db:
                db.cursor().execute(
                    """UPDATE profiles SET bio = ? WHERE id = ?""",
                    (bio, self._id)
                )
                self._bio = bio
                return True
        except Exception as e:
            print(e)
            return False
        
    def change_name(self, name: str) -> True | False:
        """
        Изменяет имя профиля пользователя
        
        :param name: новое имя пользователя
        :return: True - успех, False - возникла ошибка
        """
        try:
            with sqlite3.connect("db.db") as db:
                db.cursor().execute(
                    "UPDATE profiles SET name = ? WHERE id = ?",
                    (name, self._id)
                )
                self._name = name
                return True
        except Exception as e:
            print(e)
            return False
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def telegram_id(self) -> int:
        return self._telegram_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def bio(self) -> str:
        return self._bio
    
    @property
    def join_date(self) -> datetime.date:
        return self._join_date


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
    def __init__(self, _id: int | str):
        self._all_data = SchedulerDatabase.get_meeting_info(id=int(_id))
        self._id: int = int(_id)
        self._description: str = self.all_data[1]
        self._date_time = datetime.datetime.strptime(
            f"{self.all_data[2]} {self.all_data[3]}",
            "%d.%m.%Y %H:%M"
        )
        self._expired: bool = self.all_data[3]
    
    @staticmethod
    def get_meeting_info(id: int) -> tuple:
        """
        По полученному айди возвращает кортеж
        с информацией о встрече книжного клуба
        """
        with sqlite3.connect("db.db") as db:
            return db.cursor().execute("SELECT * FROM schedule WHERE id = ?", (id,)).fetchone()
        
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
            meetings_ds = cursor.execute("SELECT id FROM schedule WHERE expired = 0").fetchall()
            for data in meetings_ds:
                meeting = SchedulerDatabase(data[0])
                if not meeting.is_expired():
                    result.append(meeting)

        return tuple(result)
    
    @staticmethod
    def get_actual_meeting() -> tuple:
        """
        Возвращает объект класса SchedulerDatabase,
        в котором содержится информация о предстоящей встрече книжного клуба
        """
        with sqlite3.connect("db.db") as db:
            return SchedulerDatabase(
                db.cursor().execute(
                    "SELECT id FROM schedule WHERE expired = 0 ORDER BY day DESC"
                    ).fetchone()[0]
                )

    @staticmethod
    def add_meeting(
        data: list | tuple,
        reminder_function,
        ) -> True | False:
        """
        Добавляет новую встречу в таблицу расписаний
        и включает "напоминалку" об этой встрече.

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
                meeting=SchedulerDatabase(meeting_id),
                reminder_function=reminder_function
            )
            return True
            
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def add_job(
        meeting,
        reminder_function
        ) -> None:
        """
        Добавляет "работу" через библиотеку apscheduler
        :param meeting: объект класса SchedulerDatabase
        :param reminder_function: функция, отправляющая напоминание
        """
        new_job_id = "scheduler_job_" + str(meeting.id)
        info_message = f"""Информация о следующей встрече книжного клуба:
        Что на ней будет? - <b>{meeting.description}</b>
        Когда она будет? - <b>{meeting.date_time.date().strftime("%d.%m.%y")}</b>
        Во сколько приходить? - <b>{str(meeting.date_time.time())[:-3]}</b>
        """

        day, month, year = meeting.date_time.strftime("%d.%m.%Y").split(".")
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
        if self._expired is True:
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

    @property
    def description(self) -> str:
        return self._description

    @property
    def date_time(self) -> datetime.datetime:
        return self._date_time

    @property
    def all_data(self) -> tuple:
        return self._all_data


class BookDatabase(Database):
    def __init__(self, id: int):
        self._id: int = id
        self._name: str = self.get_book_info("name")
        self._description: str = self.get_book_info("description")
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
    def get_most_favorite_books_ids(amount: int) -> tuple:
        """
        Возвращает айди книг, отсортированных по их рейтингу

        :param amount - количество книг в словаре
        """
        try:
            with sqlite3.connect("db.db") as db:
                books_ids = db.cursor().execute(
                    "SELECT id FROM books ORDER BY rating DESC"
                    ).fetchall()
            return tuple(_id[0] for _id in books_ids[:abs(amount)])
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
                    rating INTEGER DEFAULT 0,
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
            has_rus_columns: bool = False,
           ) -> dict | None:
        """
        Возвращает словарь c информацией ("Имя колонки в таблицу": "информация")
        о книге или возвращает None, если возникла ошибка или книга не существует

        :param has_id: True - итог без изменений, False - айди книги не будет в итоговом словаре
        :param has_name: True - итог без изменений, False - название книги не будет в итоговом словаре
        :param has_description: True - итог без изменений, False - описание книги не будет в итоговом словаре
        :param has_image: True - итог без изменений, False - обложка книги не будет в итоговом словаре
        :param has_rus_columns: True - имена колонок будут на русском языке, False - имена колонок будут на английском языке
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
            if has_rus_columns:
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
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description