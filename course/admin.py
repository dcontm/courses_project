from django.contrib import admin
from . import models


@admin.register(models.Course)
class PlaneAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')


@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'number', 'course')


@admin.register(models.Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'open')