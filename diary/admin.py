from django.contrib import admin

from diary.models import Dish, Meal, GarminSyncedData


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("title", "calories", "protein", "fats", "carbohydrates")


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("dish", "grams", "user", "date_time")


@admin.register(GarminSyncedData)
class GarminSyncedDataAdmin(admin.ModelAdmin):
    list_display = ("id", "date_time", "user")
