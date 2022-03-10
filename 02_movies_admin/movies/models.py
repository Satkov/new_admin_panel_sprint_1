import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = "content\".\"genre"
        indexes = [models.Index(fields=['name'], name='genre_name_idx')]
        verbose_name = _('Genres')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Filmwork(UUIDMixin, TimeStampedMixin):
    TYPE_CHOICES = [
        ('movie', _('Film')),
        ('tv_show', _('TV show'))
    ]
    title = models.CharField(_('title'), max_length=100)
    description = models.CharField(_('description'), max_length=1000)
    creation_date = models.DateField(_('creation date'), null=False)
    rating = models.FloatField(_('rating'), blank=True, validators=[MinValueValidator(0),
                                                                    MaxValueValidator(100)])
    type = models.CharField(_('type'), max_length=50, choices=TYPE_CHOICES)

    class Meta:
        db_table = "content\".\"filmwork"
        indexes = [
            models.Index(fields=['title'], name='film_work_title_idx'),
            models.Index(fields=['creation_date'], name='film_work_creation_date_idx'),
        ]
        verbose_name = _('Films')
        verbose_name_plural = _('Films')

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_filmwork"
        indexes = [models.Index(fields=['film_work_id', 'genre_id'], name='genre_film_work_idx')]
        verbose_name = _('Genres')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return ''


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('full name'), max_length=50)

    class Meta:
        db_table = "content\".\"person"
        indexes = [models.Index(fields=['full_name'], name='person_full_name_idx')]
        verbose_name = _('Actor')
        verbose_name_plural = _('Actor')

    def __str__(self):
        return self.full_name


class PersonFilmWork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.TextField('role', null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_filmwork"
        indexes = [models.Index(fields=['film_work_id', 'person_id'], name='film_work_person_idx')]
        verbose_name = _('Cast')
        verbose_name_plural = _('Cast')

    def __str__(self):
        return ''
