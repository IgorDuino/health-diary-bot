from django.contrib import admin


from diary.models import Dish, Meal


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("title", "calories", "protein", "fats", "carbohydrates")


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("dish", "grams", "user")
