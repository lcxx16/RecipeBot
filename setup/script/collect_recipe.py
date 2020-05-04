from const import *
from setting import *
from dto import *
from time import sleep
import requests
import datetime


def main():
    categories = session.query(CategoryAll.large_id, CategoryAll.medium_id, CategoryAll.small_id). \
        all()

    for category in categories:
        category_id = str(category[0]) + "-" + str(category[1]) + "-" + str(category[2])

        api_url = API.FORM + category_id + API.APP
        res = requests.get(api_url)
        sleep(1.5)
        json_data = res.json()

        for rcp in json_data['result']:
            # Recipe existence check
            recipes = session.query(Recipe.recipe_name). \
                filter(Recipe.recipe_name == rcp['recipeTitle']). \
                first()

            if recipes is None:
                # Recipe insert
                recipe = Recipe()
                recipe.recipe_id = rcp['recipeId']
                recipe.recipe_name = rcp['recipeTitle']
                recipe.recipe_url = rcp['recipeUrl']
                recipe.recipe_photo = rcp['foodImageUrl']
                recipe.material = rcp['recipeMaterial']
                recipe.large_id = category[0]
                recipe.medium_id = category[1]
                recipe.small_id = category[2]
                recipe.register_date = get_datetime()
                session.add(recipe)
                session.commit()

def get_datetime():
    date = datetime.datetime.now()
    return str(date.year * 10000 + date.month * 100 + date.day)


if __name__ == "__main__":
    main()
