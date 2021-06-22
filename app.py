import os

from bson import json_util, ObjectId
from flask import Flask, render_template, request, jsonify, session, json
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from flask_socketio import SocketIO, send

load_dotenv()

app = Flask(__name__)
app.secret_key = 'e76gu687bcsk#dh@hkdk&vvb$7hvz'
socketio = SocketIO(app)

app.config["MONGO_URI"] = os.getenv('MONGO_URI')
mongo = PyMongo(app)


def parse_json(data):
    return json.loads(json_util.dumps(data))


@app.route('/')
def blog():
    user_collection = mongo.db.users
    query = {"name": "Shubham Gupta"}
    doc = user_collection.find(query)
    doc = parse_json(doc)
    session["userid"] = doc[0]["_id"]['$oid']
    user_collection = mongo.db.users_post
    results = user_collection.find().sort("_id", -1)
    return render_template('blog.html', post_data=results)


@socketio.on('message', namespace='/create_post')
def create_post(content):
    if content:
        user_collection = mongo.db.users_post
        obj = user_collection.insert_one({'content': content, 'user': session["userid"]})
        data = render_template('create_post.html', content=content, post_id=obj.inserted_id)

        send(data, broadcast=True)


@socketio.on('message', namespace='/like_post')
def like_post(post_id):
    if post_id:
        like_collection = mongo.db.likes_on_post
        count = post_like_exist(post_id)
        if count > 0:
            query = {"post_id": post_id}
            count = count+1
            update_count = {"$set": {"like_count": count}}
            like_collection.update_one(query, update_count)

        else:
            count = count + 1
            like_collection.insert_one({'post_id': post_id,
                                        'user_id': session["userid"],
                                        'like_count': count
                                        })

        data = '{"post_id": "'+post_id+'", "count": "'+str(count)+'"}'

        send(data, broadcast=True)


@app.route('/comment_on_post', methods=['POST', 'GET'])
def comment_on_post():
    if request.method == 'POST' and request.form['comment']:
        comment = request.form['comment']
        post_id = request.form['post_id']
        comments_collection = mongo.db.users_comments
        comments_collection.insert_one({'comment': comment,
                                        'user_id': session["userid"],
                                        'post_id': post_id})
        results = comments_collection.find({'post_id': post_id})
        return render_template('comments_on_post.html', results=results)
    else:
        return jsonify({"status": "fail"})


@app.route('/view_comments', methods=['POST', 'GET'])
def view_comments():
    if request.method == 'POST' and request.form['post_id']:
        post_id = request.form['post_id']
        comments_collection = mongo.db.users_comments
        results = comments_collection.find({'post_id': post_id})
        return render_template('comments_on_post.html', results=results)
    else:
        return jsonify({"status": "fail"})


def post_like_exist(post_id):
    likes_collection = mongo.db.likes_on_post
    query = {"post_id": post_id}
    if likes_collection.count_documents(query) > 0:
        doc = likes_collection.find(query)
        doc = parse_json(doc)
        return doc[0]["like_count"]

    return 0


@app.template_filter()
def get_user_name(post_id):
    post_collection = mongo.db.users_post
    query = {"_id": ObjectId(post_id)}
    post_doc = post_collection.find(query)
    post_doc = parse_json(post_doc)
    u_id = post_doc[0]["user"]

    user_collection = mongo.db.users
    query = {"_id": ObjectId(u_id)}
    doc = user_collection.find(query)
    doc = parse_json(doc)

    return doc[0]["name"]


@app.template_filter()
def count_likes(post_id):
    post_collection = mongo.db.users_post
    query = {"_id": ObjectId(post_id)}
    doc = post_collection.find(query)
    doc = parse_json(doc)

    query2 = {"post_id": doc[0]['_id']['$oid']}
    # print(query2)
    likes_collection = mongo.db.likes_on_post
    doc2 = likes_collection.find(query2)
    doc2 = parse_json(doc2)

    if doc2:
        return doc2[0]["like_count"]
    return 0


@socketio.on('message', namespace='/test')
def handle_message(data):
    print('received message: ' + data)
    send(data, broadcast=True)


if __name__ == '__main__':
    socketio.run(app)
