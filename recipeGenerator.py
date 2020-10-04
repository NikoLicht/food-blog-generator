import json
import random
import math
import re
import os
from grammarPy import Grammar
import sqlite3
import uuid
from datetime import datetime, date
from storyGenPy import Story
import holidays
import requests


connection = sqlite3.connect('./db')
cursor = connection.cursor()

data = {}
grammar = Grammar()
story = Story()
categories = []
us_holidays = holidays.CountryHoliday('US')


def generate_recipe():
    ingredients = pick_ingredients()
    main_method = random_method()
    main_prep_method_a = random_prep_method()
    main_prep_method_b = random_prep_method()
    main_plating_method = random_plating_method()
    threshold = int(math.ceil(0.5 * (len(ingredients)-1)))
    main_ingredients = ingredients[0:threshold]
    image_string = download_image(main_ingredients[0])
    secondary_prep_method_a = random_prep_method()
    secondary_prep_method_b = random_prep_method()
    secondary_method = random_method()
    secondary_plating_method = random_plating_method()
    secondary_ingredients = ingredients[threshold:]
    method_adjective_a = random_method_effect(main_method)
    method_adjective_b = random_method_effect(main_method)
    title = "{} {} {} {} {} {} {}".format(
            random_adjective(), 
            method_adjective_a,
            grammar.past_tense(main_method), 
            grammar.list_items(main_ingredients), 
            random_join_word(), 
            grammar.past_tense(secondary_method), 
            grammar.list_items(secondary_ingredients)
            )

    print (title)

    recipe_text = []
    recipe_text.append( prep_step(main_ingredients, main_prep_method_a, main_prep_method_b, main_method))
    recipe_text.append( cooking_step(main_ingredients, main_method, method_adjective_a, method_adjective_b))
    recipe_text.append( plating_step(main_ingredients, main_plating_method, main_method))
    recipe_text.append( prep_step(secondary_ingredients, secondary_prep_method_a, secondary_prep_method_b, secondary_method))
    recipe_text.append( cooking_step(secondary_ingredients, secondary_method, None, None))
    recipe_text.append( plating_step(secondary_ingredients, secondary_plating_method, secondary_method))
    recipe_text.append( final_step(title, main_method, secondary_method, main_ingredients, secondary_ingredients))

    data = {
            "title" : title,
            "recipe_text": recipe_text,
            "main_ingredients" : main_ingredients,
            "main_method" : main_method
        }
    story.set_data(data)
    story_text  = story.get_story()
    print(story_text)
    print(recipe_text)
    #                                       id, title, story, recipe, date, likes
    query = "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?)"

    cooking_text = {
            "recipe_steps" : recipe_text,
            "ingredients" : [make_ingredient_pair(ing) for ing in ingredients],
            "cooking_time": random .choice(["30 minutes", "50 mintes", "2 - 2.5 hours", "6 hours"]),
            "image_string": image_string
            }
    cooking_text_json = json.dumps(cooking_text) 
    cursor.execute(query, (str(uuid.uuid4()), title, story_text, cooking_text_json, datetime.today(), 0))
    connection.commit()

    select_query = "select * from posts"
    rows = cursor.execute(select_query).fetchall()
    #print(rows)

def prep_step(ingredients, prep_method_a, prep_method_b, cooking_method):
    prep = ""
    if len(ingredients) > 1:
        threshold = int(math.ceil(0.499999 * (len(ingredients) -1)))
        prep += "Prior to {} anything, we need to {} the {} {} ".format(grammar.ing(cooking_method), prep_method_a, grammar.list_items(ingredients[0:threshold]), random_prep_method_details(prep_method_a))
        prep += "and then we need to {} the {} {}. ".format(prep_method_b, grammar.list_items(ingredients[threshold:]), random_prep_method_details(prep_method_b))
    else:
        prep += "Before we {} the {}, we need to {} the {} {} ".format(cooking_method, ingredients[0], prep_method_a, grammar.list_items(ingredients), random_prep_method_details(prep_method_a))
        prep += "and then we {} it {}. ".format(prep_method_b, random_prep_method_details(prep_method_b))
    

    return prep
    
def cooking_step(ingredients, main_method, method_adjective_a, method_adjective_b):
    step = ""
    step += random.choice(["You guessed it, ", "All Righty, ", "Sigh, ", "Okay, ", "So, ", "Well, ", "Let's get to it, ", "Moving on, ", "Yup, ", "Continuing, "])
    step += "{} {} the {}. ".format(random_action_word(), main_method, grammar.list_items(ingredients))
    step += "We will be {} the {} {}".format(grammar.ing(main_method), grammar.list_items(ingredients), method_detail_check_for_substitution(random_method_details(main_method)))
    if method_adjective_a != None:
        alternative_cooking_time = [
            ". Alternatively we can let it {} until {}.".format(main_method, method_adjective_a),
            ". Alternatively we can let it {} until {}.".format(main_method, method_adjective_b),
            ". Alternatively we can let it {} until {} and {}.".format(main_method, method_adjective_a, method_adjective_b)
        ]
        step += random.choice(alternative_cooking_time)
    return step

def plating_step(ingredients, plating_method, cooking_method):
    starters = ["When", "After", "Later, when", "30 minutes later, when", "A glass of wine later, when"]
    step = ""
    step += "{} the {} have {} we are going to {}".format(random.choice(starters), grammar.list_items(ingredients), grammar.past_tense(cooking_method), plating_method)
    if (len(ingredients) > 1):
        step += " them all"
    else:
        step += " it"
    step += " {}.".format(random_plating_method_details(plating_method))
    return step

def final_step (title, primary_cooking_method, secondary_cooking_method, primary_ingredients, secondary_ingredients):
    step = ""
    step += "Finally we are ready to assemble and serve our {}. ".format(title.lower())
    step += random.choice(["Simply put, ", "Okay, ", "So, ", "Well, ", "Let's get to it, ", "Moving on, ", "Continuing, "])
    step += "now {}.".format(check_for_used_ingredients(grammar.list_items(primary_ingredients), grammar.list_items(secondary_ingredients), primary_cooking_method, secondary_cooking_method, random_finishing_method()))
    random_topping = random.choice([
        "$fat$", 
        "a few dashes of $spice$", 
        "a {} dollop of $condiment$".format(random.choice(["big", "small", "good", "healthy", "naughty", "frisky", "regretful", "delicious"])),
        "some slices of $fruit$",
        "some freshly grated of $vegetable$",
        "a few fresh sprigs of $herb$"
        ])
    step += method_detail_check_for_substitution(" As a final touch, i like to top this wonderful dish with {}.".format(random_topping))
    return step


def random_method():
    return random.choice(list(data['cooking_methods']))

def random_method_details(method_name):
    return random.choice(data['cooking_methods'][method_name]["modes"])

def random_method_effect(method_name):
    return random.choice(data['cooking_methods'][method_name]["effects"])

def random_prep_method():
    return random.choice(list(data['prep_methods']))

def random_prep_method_details(method_name):
    return random.choice(data['prep_methods'][method_name]["formats"])

def random_plating_method():
    return random.choice(list(data['plate_methods']))

def random_plating_method_details(method_name):
    return random.choice(data['plate_methods'][method_name]["formats"])

def random_finishing_method():
    method = random.choice(list(data['final_methods']))
    return random.choice(data['final_methods'][method]["formats"])

def random_ingredient():
    return random.choice(list(data['ingredients']))

def random_adjective():
    date_check = date.today()
    if date_check in us_holidays:
        return us_holidays.get(date_check)
    return random.choice(list(data['adjectives']))

def random_join_word():
    return random.choice(list(data['join_words']))

def random_action_word():
    return random.choice(list(data['action_words']))

def get_random_ingredient_by_type(ing_type):
    ingredients_allowed = [x for x in list(data["ingredients"]) if data["ingredients"][x]["type"] == ing_type]
    return random.choice(ingredients_allowed)

def get_random_ingredient_by_category(category):
    ingredients_allowed = [x for x in list(data["ingredients"]) if category in data["ingredients"][x]["categories"]]
    return random.choice(ingredients_allowed)

def method_detail_check_for_substitution(method_string):
    pattern = re.compile('\$[a-zA-Z]+\$')
    if len(pattern.findall(method_string)) > 0:
        substitute = pattern.search(method_string).group() 
        key = substitute[1:-1]
        new_word = "butter"
        if key in categories:
            new_word = get_random_ingredient_by_category(key)
        else:
            new_word = get_random_ingredient_by_type(key)

        string_fixed = method_string.replace(substitute, new_word)
        return string_fixed 
    else:
        return method_string

def check_for_used_ingredients(ingredients_a, ingredients_b, method_a, method_b, method_string):
    pattern = re.compile('\{[a-zA-Z]+\}')
    string_fixed = method_string
    if len(pattern.findall(method_string)) > 0:
        string_fixed = method_string.replace("{a}", grammar.past_tense(method_a) + " " + ingredients_a.lower())
        string_fixed = string_fixed.replace("{b}", grammar.past_tense(method_b) + " " + ingredients_b.lower())
    return string_fixed

def read_data():
    global data
    with open('data.json') as json_file:
        data = json.load(json_file)

def pick_ingredients():
    amount_of_ingredients = random.randint(2, 8)
    chosen_ingredients = []
    for ing in range (amount_of_ingredients):
        chosen_ingredients.append(random_ingredient())
    return chosen_ingredients

def make_ingredient_pair(ingredient):
    fluid_types = ["liquid", "gooey"]
    fluid_measurements = ["dl", "cups", "pints", "dashes", "liter", "whole"]
    non_fluid_types = ["dl", "kg", "grams", "tablespoons", "pinches", "whole"]
    measurement = random.choice(non_fluid_types)
    food_type = data["ingredients"][ingredient]["type"]
    if food_type in fluid_types:
        measurement = random. choice(fluid_measurements)
    return {
            "amount" : random_amount(),
            "measurement" : measurement,
            "ingredient" : ingredient
            }

def random_amount():
    smalls = random.randint(1, 20)
    hundreds = random.randint(1, 25) * 100
    under_one = random.choice(["Half a", "A quarter", "3/4", "1/2", "0.7"])
    return random.choice([smalls, hundreds, under_one])
    

def create_list_of_categories():
    global categories
    for ingredient in list(data["ingredients"]):
        for ing_cat in list(data["ingredients"][ingredient]["categories"]):
            if ing_cat not in categories:
                categories.append(ing_cat)

def download_image(ingredient_name):
    if not os.path.exists('./static/images/{}'.format(ingredient_name)):
        response = requests.get("https://pixabay.com/api/?key=4566006-6b87df64c2d991bb6c07d09e9&q={}&image_type=photo&pretty=true".format(ingredient_name))
        data = response.json()
        url = data["hits"][3]["webformatURL"]
        img_blob = requests.get(url, timeout=6).content
        with open ("./static/images/{}.jpg".format(ingredient_name), 'wb') as img_file:
                img_file.write(img_blob)
    return "{}.jpg".format(ingredient_name)

def main():
    read_data()
    create_list_of_categories()
    generate_recipe()


main()
