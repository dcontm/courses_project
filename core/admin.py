from django.contrib import admin
from . import models


@admin.register(models.Plane)
class PlaneAdmin(admin.ModelAdmin):
    list_display = ('title', 'period', 'price')

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email' ,'inv_near', 'inv_middle', 'inv_far', 'balanse', 'is_open', 'plane')
    search_fields = ('username__iexact', 'email__iexact')

@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'action', 'amount',)
    search_fields = ('user__username__iexact', 'user__email__iexact')
