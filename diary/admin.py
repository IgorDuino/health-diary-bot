from django.contrib import admin


from diary.models import Dish, Meal


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    pass


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    pass