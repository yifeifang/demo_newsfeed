from flask import Flask, request, jsonify
import friendDB
import redis
import uuid
import pickle
import pika
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

####################################################### Handle rabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', heartbeat=600,
                                       blocked_connection_timeout=3000))
channel = connection.channel()
channel.queue_declare(queue='FanoutMQ')

######################################################## Handle post
# A dictionary to store the postDB posted by the user
postDB = redis.Redis(host='localhost', port=6379, db=0)

# A route to handle POST requests to v1/me/feed
@app.route("/v1/me/feed", methods=["POST"])
def post_feed():
    # Get the content and user from the request body
    content = request.form.get("content")
    user = request.form.get("user")
    post_uuid = uuid.uuid4().hex
    print(user, content)
    # Validate the user
    if not user in friendDB.get_users():
        return jsonify({"error": "User not exist"}), 401

    # Store the content in the postDB dictionary with the user as the key
    postDB.set(post_uuid, pickle.dumps((user, content)))

    try:
        friends = friendDB.get_friends(user)
        print(friends)
        channel.basic_publish(exchange='',
                        routing_key='FanoutMQ',
                        body=pickle.dumps([post_uuid, friends]))
    except ValueError as e:
        # Handle any error from the friends module
        return jsonify({"error": str(e)}), 400
    
    # Return a success message
    return jsonify({"message": "Feed posted successfully"}), 201

# A route to handle GET requests to v1/me/feed
@app.route("/v1/me/feed", methods=["GET"])
def get_feed():
    # Get the user from the request header
    user = request.args.get("user")
    # Validate the user
    if not user in friendDB.get_users():
        return jsonify({"error": "User not exist"}), 401

    feedcache = None
    with open("feedcache", "rb") as f:
        feedcache = pickle.load(f)

    print(feedcache)
    if user in feedcache:
        feedsdict = feedcache[user]
    else:
        return jsonify({"error": "No feed for the current user"}), 404
    
    # Get the content from the postDB dictionary with the user as the key
    content_list = []
    print(feedsdict)
    for feed_uuid in feedsdict:
        print(feed_uuid)
        content = pickle.loads(postDB.get(feed_uuid))
        # If no content is found, return an error message
        if not content:
            return jsonify({"error": "No feed found"}), 404
        content_list.append(content)

    # Return the content as a json object
    return jsonify({"content": content_list}), 200

######################################################## Handle Friend ship

# A route to handle GET requests to /users/create?name=<name>
@app.route("/users/create", methods=["GET"])
def create_user():
    # Get the name from the query parameter
    name = request.args.get("name")
    # Create a new user using the friendDB module
    try:
        friendDB.create_user(name)
    except ValueError as e:
        # Handle any error from the friendDB module
        return jsonify({"error": str(e)}), 400
    # Return a success message with the user name
    return jsonify({"message": "User created successfully", 
                    "user": name}), 201

# A route to handle GET requests to /users
@app.route("/users", methods=["GET"])
def get_users():
    # Get all the users from the friendDB module
    users = friendDB.get_users()
    # Return the users as a json object
    return jsonify({"users": users}), 200

# A route to handle GET requests to /users/<name>/friends
@app.route("/users/<name>/friends", methods=["GET"])
def get_friends(name):
    # Get the friends of the user from the friendDB module
    try:
        friends = friendDB.get_friends(name)
    except ValueError as e:
        # Handle any error from the friends module
        return jsonify({"error": str(e)}), 400
    # Return the friends as a json object
    return jsonify({"friends": friends}), 200

# A route to handle GET requests to /users/<name>/friends/add?friend=<friend>
@app.route("/users/<name>/friends/add", methods=["GET"])
def add_friend(name):
    # Get the friend name from the query parameter
    friend = request.args.get("friend")
    # Add a friend to the user using the friendDB module
    try:
        friendDB.add_friend(name, friend)
    except ValueError as e:
        # Handle any error from the friendDB module
        return jsonify({"error": str(e)}), 400
    # Return a success message with the user and friend names
    return jsonify({"message": "Friend added successfully", 
                    "user": name, 
                    "friend": friend}), 201

if __name__ == "__main__":
    app.run(debug=True)
