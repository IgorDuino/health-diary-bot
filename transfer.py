import pandas as pd
from diary.models import Dish

df = pd.read_excel("dishes.xlsx")

for index, row in df.iterrows():
    t = row["Продукт"]
    if isinstance(t, str) and t:
        dish = Dish(
            title=row["Продукт"][6:],
            grams=row["Вес, г"],
            calories=row["Калорийность, ккал"],
            protein=row["Белок, г"],
            fats=row["Жир общий, г"],
            carbohydrates=row["Углеводы, по разности, г"],
        )
        dish.save()