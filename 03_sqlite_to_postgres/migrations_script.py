import sqlite3
from dataclasses import dataclass

con = sqlite3.connect('db.sqlite')
cur = con.cursor()


def get_data_from_table(table):
    cur.execute(f"SELECT * FROM {table}")
    while True:
        results = cur.fetchmany(1000)
        if not results:
            break
        for result in results:
            yield result


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


if __name__ == '__main__':
    persons = fill_dataclass(get_data_from_table('person'), Person)
    genres = fill_dataclass(get_data_from_table('genre'), Genre)
    film_works = fill_dataclass(get_data_from_table('film_work'), Filmwork)
    person_film_works = fill_dataclass(get_data_from_table('person_film_work'), PersonFilmWork)
    genre_film_works = fill_dataclass(get_data_from_table('genre_film_work'), GenreFilmwork)
    cur.close()
    for i in film_works:
        print(i)
    print(len(persons))