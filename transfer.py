import pandas as pd
from diary.models import Dish

df = pd.read_excel('КроссТаблица.xlsx')
data = []
for index, row in df.iterrows():
    dish = Dish(
        title=row['Продукт'][6:],
        grams=row['Вес, г'],
        calories=row['Калорийность, ккал'],
        protein=row['Белок, г'],
        fats=row['Жир общий, г'],
        carbohydrates=row['Углеводы, по разности, г']
    )
    data.append(dish)

Dish.objects.bulk_create(data)