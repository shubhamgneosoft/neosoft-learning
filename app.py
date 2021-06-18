import os
from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["MONGO_URI"] = os.getenv('MONGO_URI')
mongo = PyMongo(app)


@app.route('/')
def blog():
    return render_template('blog.html')


@app.route('/create_post', methods=['POST', 'GET'])
def create_post():
    if request.method == 'POST' and request.form['content']:
        content = request.form['content']
        user_collection = mongo.db.users_post
        user_collection.insert({'name': 'Shubham Gupta', 'content': content})
        return render_template('create_post.html', content=content)
    else:
        return jsonify({"status": "fail"})


@app.route('/adduser')
def index():
    user_collection = mongo.db.users
    user_collection.insert({'name': 'shubham3'})
    return '<html><body><h1>user added</h1></body></html>'


if __name__ == '__main__':
   app.run(debug = True)