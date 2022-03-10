import datetime
import sqlite3
import uuid

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from dataclasses import dataclass


@dataclass(frozen=True)
class Person:
    __slots__ = ('id', 'full_name', 'created', 'modified')
    id: uuid
    full_name: str
    created: datetime
    modified: datetime


@dataclass(frozen=True)
class Genre:
    __slots__ = ('id', 'name', 'description')
    id: uuid
    name: str
    description: str


@dataclass(frozen=True)
class GenreFilmwork:
    __slots__ = ('id', 'film_work', 'genre', 'created')
    id: uuid
    film_work: uuid
    genre: uuid
    created: datetime


@dataclass(frozen=True)
class PersonFilmWork:
    __slots__ = ('id', 'film_work', 'person', 'role', 'created')
    id: str
    film_work: str
    person: str
    role: str
    created: str


@dataclass(frozen=True)
class Filmwork:
    id: uuid
    title: str
    description: str
    creation_date: datetime
    rating: float
    type: str
    created: datetime
    modified: datetime


def get_data_from_table(table, cursor):
    cursor.execute(f"SELECT * FROM {table}")
    while True:
        results = cursor.fetchmany(1000)
        if not results:
            break
        for result in results:
            yield result


def fill_dataclass(data, table):
    result = []
    if table == Person or table == GenreFilmwork:
        for fields in data:
            T = table(fields[0], fields[1], fields[2], fields[3])
            result.append(T)
    if table == Genre:
        for fields in data:
            T = table(fields[0], fields[1], fields[2])
            result.append(T)
    if table == PersonFilmWork:
        for fields in data:
            T = table(fields[0], fields[1], fields[2], fields[3], fields[4])
            result.append(T)
    if table == Filmwork:
        for fields in data:
            T = table(fields[0], fields[1], fields[2], fields[3], fields[5], fields[6], fields[7], fields[8])
            result.append(T)
    return result


def execute_migration(table, fields, data, pg_cursor):
    format_symbols = '%s, ' * len(fields.split(','))
    args = ','.join(pg_cursor.mogrify(f"({format_symbols[:-2]})",
                                      item).decode() for item in data)
    sql = (f"""
        INSERT INTO content.{table} ({fields})
        VALUES {args}
        ON CONFLICT (id) DO NOTHING
        """)
    pg_cursor.execute(sql)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    sqlite_cursor = connection.cursor()
    persons = fill_dataclass(get_data_from_table('person', sqlite_cursor), Person)
    genres = fill_dataclass(get_data_from_table('genre', sqlite_cursor), Genre)
    film_works = fill_dataclass(get_data_from_table('film_work', sqlite_cursor), Filmwork)
    person_film_works = fill_dataclass(get_data_from_table('person_film_work', sqlite_cursor), PersonFilmWork)
    genre_film_works = fill_dataclass(get_data_from_table('genre_film_work', sqlite_cursor), GenreFilmwork)
    sqlite_cursor.close()

    pg_cursor = pg_conn.cursor()

    pg_cursor.execute("""TRUNCATE content.person CASCADE""")
    pg_cursor.execute("""TRUNCATE content.filmwork CASCADE""")
    pg_cursor.execute("""TRUNCATE content.genre CASCADE""")

    # Person
    data = [(item.id, item.full_name, item.created, item.modified) for item in persons]
    columns = 'id, full_name, created, modified'
    execute_migration('Person', columns, data, pg_cursor)

    # Filmwork
    data = [(item.id, item.title, item.description, item.creation_date,
            item.rating, item.type, item.created, item.modified) for item in film_works]
    columns = 'id, title, description, creation_date, rating, type, created, modified'
    execute_migration('filmwork', columns, data, pg_cursor)
    #
    # Genre
    data = [(item.id, item.name, item.description) for item in genres]
    columns = 'id, name, description'
    execute_migration('genre', columns, data, pg_cursor)

    # Person_filmwork
    data = [(item.id, item.film_work, item.person, item.role, item.created) for item in person_film_works]
    columns = 'id, film_work_id, person_id, role, created'
    execute_migration('person_filmwork', columns, data, pg_cursor)

    # Genre_filmwork
    data = [(item.id, item.film_work, item.genre, item.created) for item in genre_film_works]
    columns = 'id, film_work_id, genre_id, created'
    execute_migration('genre_filmwork', columns, data, pg_cursor)

    # print(args)
    connection.commit()


if __name__ == '__main__':
    dsl = {'dbname': 'movies_database', 'user': 'app', 'password': '123qwe', 'host': '127.0.0.1', 'port': 5432}
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
