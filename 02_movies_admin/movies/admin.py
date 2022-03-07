from django.contrib import admin
from .models import Genre, Filmwork, GenreFilmwork, Person, PersonFilmWork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmWorkInline,)
    list_display = ('title', 'type', 'creation_date', 'rating',)
    list_filter = ('type',)
    search_fields = ('title', 'genres__name')
    date_hierarchy = 'creation_date'
    ordering = ('-creation_date', '-rating',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = (PersonFilmWorkInline,)
    list_display = ('full_name',)
    search_fields = ('full_name',)
    ordering = ('full_name',)
