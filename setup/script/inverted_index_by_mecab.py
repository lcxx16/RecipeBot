from const import *
from setting import *
from dto import *
import MeCab

def main():
    # ** MeCab conf ** 
    tagger = MeCab.Tagger('-Ochasen')

    # ** select recipe_number, material from recipe ; **
    recipes = session.query(Recipe.recipe_number, Recipe.material). \
                all()
    
    for recipe in recipes:
        result = tagger.parse(recipe.material)
        lines = result.split('\n')

        for line in lines:
            line_array = line.split('\t')

            if line_array[0] == 'EOS':
                break

        for result in results:
            # ** select * from inverted_index where index_kana = ? ; **
            registered_index = session.query(InvertedIndex). \
                filter(InvertedIndex.index_bigram == result). \
                first()

            if registered_index is None:
                inverted_index = InvertedIndex()
                inverted_index.index_kana = line_array[1]
                inverted_index.index_category = line_array[3]
                inverted_index.index = recipe.recipe_number
                session.add(inverted_index)
                session.commit()
            else:
                index = registered_index.index.split(',')
                if index[len(index) - 1] == str(recipe.recipe_number):
                    break
                
                registered_index.index += ',' + str(recipe.recipe_number)
                session.commit

if __name__ == "__main__":
    main()
