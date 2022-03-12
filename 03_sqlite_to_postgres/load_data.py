import os
import sqlite3

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from table_objects import (Filmwork, Genre, GenreFilmwork, Person,
                           PersonFilmWork)


def get_data_from_table(table, cursor):
    """

    @param table: str
    @param cursor: cursor_object
    @return: generator
    """
    cursor.execute(f"SELECT * FROM {table}")
    while True:
        results = cursor.fetchmany(1000)
        if not results:
            break
        for result in results:
            yield result


def fill_dataclass(data, table):
    """

    @param data: generator
    @param table: class
    @return: list[class_objects]
    """
    result = []
    for columns in data:
        fields = {
            Person: ['id', 'full_name', 'created', 'modified'],
            GenreFilmwork: ['id', 'film_work', 'genre', 'created'],
            Genre: ['id', 'name', 'description', 'created', 'updated'],
            PersonFilmWork: ['id', 'film_work', 'person', 'role', 'created'],
            Filmwork: ['id', 'title', 'description', 'creation_date',
                       'file_path', 'rating', 'type', 'created', 'modified']
        }
        Table = table()
        for column_data in columns:
            field_name = fields[table].pop(0)
            setattr(Table, field_name, column_data)
        result.append(Table)

    return result


def execute_migration(table, columns, data, pg_cursor):
    """

    @param table: str
    @param columns: str
    @param data: list[tuple(str)]
    @param pg_cursor: cursor_object
    """
    format_symbols = '%s, ' * len(columns.split(','))
    args = ','.join(pg_cursor.mogrify(f"({format_symbols[:-2]})", item).decode() for item in data)
    sql = (f"""
        INSERT INTO content.{table} ({columns})
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

    pg_cursor.execute("""TRUNCATE content.person, content.filmwork, content.genre CASCADE""")

    # Person
    data = [(item.id, item.full_name, item.created, item.modified) for item in persons]
    columns = 'id, full_name, created, modified'
    execute_migration('Person', columns, data, pg_cursor)

    # Filmwork
    data = [(item.id, item.title, item.description, item.creation_date,
             item.rating, item.type, item.created, item.modified) for item in film_works]
    columns = 'id, title, description, creation_date, rating, type, created, modified'
    execute_migration('filmwork', columns, data, pg_cursor)

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

    connection.commit()


if __name__ == '__main__':
    load_dotenv()
    dsl = {'dbname': os.environ.get('DB_NAME'), 'user': os.environ.get('DB_USER'),
           'password': os.environ.get('DB_PASSWORD'), 'host': os.environ.get('DB_HOST'),
           'port': os.environ.get('DB_PORT')}
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
