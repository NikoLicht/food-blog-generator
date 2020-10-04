import re
import pickle
import json
import random
import sqlite3
from grammarPy import Grammar

link = "makenews.com/"
class Story:
    data = {}
    story_data = {}
    grammar = None
    cursor = None
    connection = None
    saved_data = None
    special_story_triggered = None

    def __init__(self, *args, **kwargs):
        global grammar, cursor, connection, link, saved_data
        grammar = Grammar()
        connection = sqlite3.connect('./db')


        cursor = connection.cursor()
        with open('private_life.json') as json_file:
            self.story_data = json.load(json_file)
            
        #saving data or creating default data
        self.saved_data = self.get_default_data()
        try:
            self.saved_data = pickle.load(open("saved_data.pickle", "rb"))
        except (OSError, IOError) as e:
            pickle.dump(self.saved_data, open("saved_data.pickle", "wb"))

    def get_story(self):
        start = self.replace_tags(random.choice(list(self.story_data["intro"])))
        family_text = self.replace_tags(random.choice(list(self.story_data["family_text"]))) 
        end = self.replace_tags(random.choice(list(self.story_data["ending"]))) 

        if self.special_story_triggered == None:
            return start + " " + family_text + " " + end
        else:
            return self.replace_tags(random.choice(list(self.story_data["special_story"][self.special_story_triggered]))) 
    
    def replace_tags(self, text):
        global link
        text = self.register_action(text)
        pattern = re.compile('\$([a-zA-Z]+|[a-zA-Z]+_[a-zA-Z]+)\$')
        if len(pattern.findall(text)) > 0:
            substitute = pattern.search(text).group() 
            key = substitute[1:-1] #cutting of the $$
            tag_replacement = None

            if key == "son":
                tag_replacement = self.story_data["family"]["son"]["name"]

            elif key == "daughter":
                tag_replacement = self.story_data["family"]["daughter"]["name"]

            elif key == "husband":
                tag_replacement = self.story_data["family"]["husband"]["name"]
                if self.saved_data["husband_cheated"] > 4:
                    tag_replacement = "ex-husband"

            elif key == "one_child":
                tag_replacement = random.choice([self.story_data["family"]["daughter"]["name"], self.story_data["family"]["son"]["name"]])

            elif key == "husband_act":
                tag_replacement = random.choice(self.story_data["husband_act"])

            elif key == "family_member":
                person = random.choice(list(self.story_data["family"]))
                name = self.story_data["family"][person]["name"]
                postfix = ", my " + person + ","
                tag_replacement = random.choice([name, name + postfix, "My " + person + ","])

            elif key == "dish_description":
                tag_replacement = random.choice(self.story_data["dish_description"])

            elif key == "random_dish":
                select_query = "SELECT * FROM POSTS ORDER BY RANDOM() LIMIT 1"
                row = cursor.execute(select_query).fetchall()
                tag_replacement = '<a href="{}" >{}</a>'.format(link + str(row[0][0]), row[0][1])

            elif key == "title":
                tag_replacement = self.data["title"]

            elif key == "cooked_main":
                ing = random.choice(self.data["main_ingredients"])
                method = self.data["main_method"]
                tag_replacement = grammar.past_tense(method) + " " + ing

            elif key == "lady":
                tag_replacement = random.choice(self.story_data["ladies"])

            if tag_replacement != None:
                text_replaced = text.replace(substitute, tag_replacement)
            else:
                print ("You need to handle tag: " + key)

            if len(pattern.findall(text_replaced)) > 0:
                text_replaced = self.replace_tags(text_replaced)
            return text_replaced

        else:
            return text

    def register_action(self, text):
        pattern = re.compile('\%([a-zA-Z]+|[a-zA-Z]+_[a-zA-Z]+)\%')
        changed_text = text
        if len(pattern.findall(text)) > 0:
            substitute = pattern.search(text).group() 
            key = substitute[1:-1] #cutting of the %%

            if key == "husband_cheated":
                print (self.saved_data)
                print (self.saved_data[key])
                self.saved_data[key] += 1
                print ("husband has cheated {} times".format(self.saved_data["husband_cheated"]))
                if self.saved_data["husband_cheated"] == 4:
                    self.special_story_triggered = "husband_cheated"

                self.save_data_locally()              

            changed_text = text.replace(substitute, "")
            if len(pattern.findall(changed_text)) > 0:
                changed_text = self.register_action(changed_text)

        return changed_text
    
    def get_default_data(self):
        return {
                "husband_cheated" : self.get_default_value("husband_cheated"),
                "last_treatment" : self.get_default_value("last_treatment"),
                "last_disease" : self.get_default_value("last_disease")
            }
        
    def get_default_value(self, key):
        return self.story_data["default_data"][key]

    def save_data_locally(self):
            pickle.dump(self.saved_data, open("saved_data.pickle", "wb"))

    def set_data(self, data):
        self.data = data
