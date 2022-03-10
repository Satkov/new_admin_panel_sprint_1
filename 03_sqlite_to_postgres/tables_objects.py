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
    description: strf


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