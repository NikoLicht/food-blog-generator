from flask import Flask, render_template
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)
connection = sqlite3.connect('./db', check_same_thread=False)
cursor = connection.cursor()

@app.route('/')
def home():
    query = "SELECT * FROM posts ORDER BY date DESC LIMIT 20"
    result = cursor.execute(query).fetchall()
    unpacked_posts = [unpack_post(x) for x in result]
    return render_template('home.html', posts=unpacked_posts)


def unpack_post(post):
    cooking_text = json.loads(post[3])
    print(type(post[4]))
    print(post[4])
    post = {
        "id" : post[0],
        "title" : post[1],
        "story" : post[2],
        "ingredients" : cooking_text["ingredients"],
        "steps" : cooking_text["recipe_steps"],
        "cooking_time" : cooking_text["cooking_time"],
        "image_string" : cooking_text["image_string"],
        "date" : "{:%B %d, %Y}".format(datetime.strptime(post[4], "%Y-%m-%d %H:%M:%S.%f"))
    }
    return post
