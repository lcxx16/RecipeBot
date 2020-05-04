import requests
from const import *
from setting import *
from dto import *

def main():
    api_url = CategoryAPI.FORM
    res = requests.get(api_url)
    json_data = res.json()

    loop_count = 1
    for category_kind in json_data['result']:
        for category in json_data['result'][category_kind]:

            category_dto = Category()
            category_dto.category = loop_count
            category_dto.category_id = category['categoryId']
            category_dto.category_name = category['categoryName']
            category_dto.category_url = category['categoryUrl']
            if loop_count != 3:
                category_dto.parent_category = category['parentCategoryId']

            session.add(category_dto)
            session.commit()

        loop_count = loop_count + 1


if __name__ == "__main__":
    main()