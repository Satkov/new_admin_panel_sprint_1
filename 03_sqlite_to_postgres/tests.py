import sqlite3

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from load_data import get_data_from_table
from table_objects import (Filmwork, Genre, GenreFilmwork, Person,
                           PersonFilmWork)


def count_records_in_table(table, cursor):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0]


def get_all_ids_from_table(table, cursor):
    cursor.execute(f"SELECT id  FROM {table}")
    return cursor.fetchone()


def test_number_of_records_are_same_in_both_tables(connection: sqlite3.Connection, pg_conn: _connection):
    tables = {
        'film_work': 'content.filmwork',
        'genre': 'content.genre',
        'genre_film_work': 'content.genre_filmwork',
        'person': 'content.person',
        'person_film_work': 'content.person_filmwork'
    }

    sqlite_cursor = connection.cursor()
    pg_cursor = pg_conn.cursor()

    for sqlite_table in tables.keys():
        sqlite_records = count_records_in_table(sqlite_table, sqlite_cursor)
        pg_records = count_records_in_table(tables[sqlite_table], pg_cursor)
        assert sqlite_records == pg_records, f'Количество записей в таблицах в колонке "{sqlite_table}" не совпадают'


def fill_sqlite_dataclass(data, table):
    """
    result: {Table_id: TableObj}
    Привожу дату в таблицах к единому формату и помещаю в словарь.
    """
    result = {}
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
            if field_name in ['created', 'updated', 'creation_date', 'modified'] and column_data is not None:
                setattr(Table, field_name, column_data[:-3])
            else:
                setattr(Table, field_name, column_data)
        result[Table.id] = Table

    return result


def fill_pg_dataclass(data, table):
    """
    result: {Table_id: TableObj}
    """
    result = {}
    for columns in data:
        fields = {
            Person: ['created', 'modified', 'id', 'full_name'],
            GenreFilmwork: ['id', 'created', 'film_work', 'genre'],
            Genre: ['id', 'name', 'description'],
            PersonFilmWork: ['id', 'role', 'created', 'film_work', 'person'],
            Filmwork: ['created', 'modified', 'id', 'title',
                       'description', 'creation_date', 'rating', 'type']
        }
        Table = table()
        for column_data in columns:
            field_name = fields[table].pop(0)
            if field_name in ['created', 'updated', 'creation_date', 'modified'] and column_data is not None:
                setattr(Table, field_name, column_data.strftime("%Y-%m-%d %H:%M:%S.%f"))
            else:
                setattr(Table, field_name, column_data)
        result[Table.id] = Table

    return result


def test_column_content_is_same(connection: sqlite3.Connection, pg_conn: _connection):
    sqlite_cursor = connection.cursor()
    pg_cursor = pg_conn.cursor()

    tables = {
        'film_work': 'content.filmwork',
        'genre': 'content.genre',
        'genre_film_work': 'content.genre_filmwork',
        'person': 'content.person',
        'person_film_work': 'content.person_filmwork'
    }
    table_objs = {
        'film_work': Filmwork,
        'genre': Genre,
        'genre_film_work': GenreFilmwork,
        'person': Person,
        'person_film_work': PersonFilmWork
    }

    for sqlite_table in tables.keys():
        sql_data = get_data_from_table(sqlite_table, sqlite_cursor)
        pg_data = get_data_from_table(tables[sqlite_table], pg_cursor)

        sqlite_data_objs = fill_sqlite_dataclass(sql_data, table_objs[sqlite_table])
        pg_data_objs = fill_pg_dataclass(pg_data, table_objs[sqlite_table])

        ids = get_all_ids_from_table(sqlite_table, sqlite_cursor)
        for id in ids:
            assert sqlite_data_objs[id] == pg_data_objs[id], f'Значения полей в записи {id} различаются'


if __name__ == '__main__':
    dsl = {'dbname': 'movies_database', 'user': 'app', 'password': '123qwe', 'host': '127.0.0.1', 'port': 5432}
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        test_number_of_records_are_same_in_both_tables(sqlite_conn, pg_conn)
        test_column_content_is_same(sqlite_conn, pg_conn)
