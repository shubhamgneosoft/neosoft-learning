import os
import re

from bson import json_util, ObjectId
from flask import Flask, render_template, request, jsonify, session, json, url_for, session
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from flask_socketio import SocketIO, send, emit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from flask_session import Session

load_dotenv()

app = Flask(__name__)
app.secret_key = 'e76gu687bcsk#dh@hkdk&vvb$7hvz'
socketio = SocketIO(app)

app.config["MONGO_URI"] = os.getenv('MONGO_URI')
app.config['SESSION_PERMANENT'] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
mongo = PyMongo(app)


def is_login():
    is_user = False
    userid = session.get("userid")
    loggedin = session.get("loggedin")
    if userid and loggedin:
        user_collection = mongo.db.users
        query = {"_id": ObjectId(session.get("userid"))}
        account = user_collection.count_documents(query)
        if account > 0:
            is_user = True

    return is_user


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('loggedin'):
        return redirect(url_for('blog'))
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        user_collection = mongo.db.users
        find_query = {"email": email}
        account = user_collection.count_documents(find_query)
        if account > 0:
            doc = user_collection.find(find_query)
            doc = parse_json(doc)
            db_password = doc[0]['password']
            # if password == db_password:
            if check_password_hash(db_password, password):
                session['loggedin'] = True
                session['name'] = doc[0]['name']
                session["userid"] = doc[0]["_id"]['$oid']
                return redirect(url_for('blog'))
            else:
                msg = 'Incorrect username / password !'

        else:

            msg = 'Account does not exists !'
    return render_template('login.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        name = request.form['name']
        password = request.form['password']
        con_password = request.form['con_password']
        email = request.form['email']
        user_collection = mongo.db.users
        find_query = {"email": email}
        account = user_collection.count_documents(find_query)

        if account > 0:
            msg = 'Account already exists !'
        elif not name or not password or not email:
            msg = 'Please fill out the form !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Name must contain only characters and numbers !'
        elif password != con_password:
            msg = 'Password and confirm  password does not match !'
        else:
            hashed_password = generate_password_hash(password)
            insert_query = {"name": name, "email": email, "password": hashed_password}
            user_collection.insert_one(insert_query)
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('name', None)
    resp = app.make_response(render_template('login.html'))
    resp.set_cookie('loggedin', expires=0)
    return resp
    # return redirect(url_for('login'))


def parse_json(data):
    return json.loads(json_util.dumps(data))


@app.route('/blog')
@app.route('/post/<mypost>')
@app.route('/post/<mypost>/<page>')
@app.route('/blog/<page>')
def blog(mypost=None, page=1):

    per_page_post = 5
    end = int(page)*per_page_post
    start = end - per_page_post
    requested_page = '/blog'

    if not session.get('loggedin'):
        return redirect(url_for('login'))

    elif mypost == 'mypost':
        post_collection = mongo.db.users_post
        results = post_collection.find({'user': session.get("userid")}).sort("_id", -1)[start:end]
    else:
        post_collection = mongo.db.users_post
        results = post_collection.find().sort("_id", -1)[start:end]
    if mypost == 'mypost':
        requested_page = '/post/mypost'

    return render_template('blog.html', post_data=results, page=page, requested_page=requested_page)


@socketio.on('message', namespace='/create_post')
def create_post(content):
    """

    :param content: Text
    :return: Html
    """
    if content and is_login:
        post_collection = mongo.db.users_post
        obj = post_collection.insert_one({'content': content, 'user': session.get("userid")})
        data = render_template('create_post.html', content=content, post_id=obj.inserted_id)

        send(data, broadcast=True)


@socketio.on('like_event', namespace='/like_post')
def like_post(json_req):
    post_id = json_req['post_id']
    if post_id and is_login:
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
                                        'user_id': session.get("userid"),
                                        'like_count': count
                                        })

        data = {"post_id": post_id, "count": count}
        emit('like_response', data, broadcast=True)


@socketio.on('comment_event', namespace='/comment_on_post')
def comment_on_post(json_req):
    comment = json_req['comment']
    post_id = json_req['post_id']
    if comment and post_id and is_login:
        comments_collection = mongo.db.users_comments
        comments_collection.insert_one({'comment': comment,
                                        'user_id': session.get("userid"),
                                        'post_id': post_id})
        results = comments_collection.find({'post_id': post_id})
        comments = render_template('comments_on_post.html', results=results)
        data = {"post_id": post_id, "comments": comments}

        emit('comments_response', data, broadcast=True)


@app.route('/view_comments', methods=['POST', 'GET'])
def view_comments():
    if request.method == 'POST' and request.form['post_id'] and is_login:
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
def get_user_name_by_uid(u_id):

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
