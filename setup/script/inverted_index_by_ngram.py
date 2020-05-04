from const import *
from setting import *
from dto import *

def main():
    # ** select recipe_number, material from recipe ; **
    recipes = session.query(Recipe.recipe_number, Recipe.material). \
                all()
    
    for recipe in recipes:
        # N-gram
        results = n_gram(recipe.material, 2)

        for result in results:
            # ** select * from inverted_index where index_kana = ? ; **
            registered_index = session.query(InvertedIndex3). \
                filter(InvertedIndex3.index_bigram == result). \
                first()

            if registered_index is None:
                inverted_index = InvertedIndex3()
                inverted_index.index_bigram = result
                inverted_index.index = recipe.recipe_number
                session.add(inverted_index)
                session.commit()
            else:
                index = registered_index.index.split(',')
                if index[len(index) - 1] == str(recipe.recipe_number):
                    break
                
                registered_index.index += ',' + str(recipe.recipe_number)
                session.commit


def n_gram(target, n):
    result = []
    for i in range(0, len(target) - n + 1):
        result.append(target[i:i + n])

    return result


if __name__ == "__main__":
    main()
