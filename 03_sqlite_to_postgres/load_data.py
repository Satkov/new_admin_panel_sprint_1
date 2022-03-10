import sqlite3

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from dataclasses import dataclass


@dataclass(frozen=True)
class Person:
    __slots__ = ('id', 'full_name', 'created', 'modified')
    id: str
    full_name: str
    created: str
    modified: str


@dataclass(frozen=True)
class Genre:
    __slots__ = ('id', 'name', 'description')
    id: str
    name: str
    description: str


@dataclass(frozen=True)
class GenreFilmwork:
    __slots__ = ('id', 'film_work', 'genre', 'created')
    id: str
    film_work: str
    genre: str
    created: str


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
    __slots__ = ('id', 'title', 'description', 'creation_date', 'rating', 'type', 'created', 'modified')
    id: str
    title: str
    description: str
    creation_date: str
    rating: str
    type: str
    created: str
    modified: str


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

    # data = [f"{item.id} | {item.full_name} | {item.created} | {item.modified}" for item in persons]
    # args = ','.join(pg_cursor.mogrify("(%s, %s, %s, %s)", item.split(' | ')).decode() for item in data)
    # pg_cursor.execute(f"""
    #     INSERT INTO content.Person (id, full_name, created, modified)
    #     VALUES {args}
    #     ON CONFLICT (id) DO NOTHING
    #     """)

    data = [f"{item.id} | {item.title} | {item.description} | {item.creation_date} | "
            f"{item.rating} | {item.type} | {item.created} | {item.modified}" for item in film_works]
    args = ','.join(pg_cursor.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s)",
                                      item.split(' | ')).decode() for item in data)
    pg_cursor.execute(f"""
        INSERT INTO content.filmwork (id, title, description, creation_date, rating, type, created, modified)
        VALUES {args}
        ON CONFLICT (id) DO NOTHING
        """)
    #
    # data = [f"{item.id} | {item.name} | {item.description}" for item in genres]
    # args = ','.join(pg_cursor.mogrify("(%s, %s, %s)", item.split(' | ')).decode() for item in data)
    # pg_cursor.execute(f"""
    #     INSERT INTO content.genre (id, name, description)
    #     VALUES {args}
    #     ON CONFLICT (id) DO NOTHING
    #     """)
    #
    # data = [f"{item.id} | {item.film_work} | {item.person} | {item.role} | {item.created}" for item in person_film_works]
    # args = ','.join(pg_cursor.mogrify("(%s, %s, %s, %s, %s)", item.split(' | ')).decode() for item in data)
    # pg_cursor.execute(f"""
    #         INSERT INTO content.person_filmwork (id, film_work, person, role, created)
    #         VALUES {args}
    #         ON CONFLICT (id) DO NOTHING
    #         """)
    #
    # data = [f"{item.id} | {item.film_work} | {item.genre} | {item.created}" for item in genre_film_works]
    # args = ','.join(pg_cursor.mogrify("(%s, %s, %s, %s)", item.split(' | ')).decode() for item in data)
    # pg_cursor.execute(f"""
    #             INSERT INTO content.person_filmwork (id, film_work, genre, created)
    #             VALUES {args}
    #             ON CONFLICT (id) DO NOTHING
    #             """)

    # print(args)

if __name__ == '__main__':
    dsl = {'dbname': 'movies_database', 'user': 'app', 'password': '123qwe', 'host': '127.0.0.1', 'port': 5432}
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
