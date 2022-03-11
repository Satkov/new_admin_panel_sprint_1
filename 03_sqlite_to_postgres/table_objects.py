import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass()
class Person:
    id: uuid = field(default=None)
    full_name: str = field(default=None)
    created: datetime = field(default=None)
    modified: datetime = field(default=None)


@dataclass()
class Genre:
    id: uuid = field(default=None)
    name: str = field(default=None)
    description: str = field(default=None)
    created: datetime = field(default=None)
    updated: datetime = field(default=None)

    def __eq__(self, other):
        """ Убрал лишние поля для удобства сравнения в тестировии """
        return False not in (
            self.id == other.id, self.name == other.name,
            self.description == other.description,
        )


@dataclass()
class GenreFilmwork:
    id: uuid = field(default=None)
    film_work: uuid = field(default=None)
    genre: uuid = field(default=None)
    created: datetime = field(default=None)


@dataclass()
class PersonFilmWork:
    id: str = field(default=None)
    film_work: str = field(default=None)
    person: str = field(default=None)
    role: str = field(default=None)
    created: str = field(default=None)


@dataclass()
class Filmwork:
    id: uuid = field(default=None)
    title: str = field(default=None)
    description: str = field(default=None)
    creation_date: datetime = field(default=None)
    file_path: str = field(default=None)
    rating: float = field(default=None)
    type: str = field(default=None)
    created: datetime = field(default=None)
    modified: datetime = field(default=None)

    def __eq__(self, other):
        """ Убрал лишние поля для удобства сравнения в тестировии """
        return False not in (
            self.id == other.id, self.title == other.title, self.description == other.description,
            self.creation_date == other.creation_date, self.rating == other.rating,
            self.type == other.type, self.created == other.created, self.modified == other.modified
        )
