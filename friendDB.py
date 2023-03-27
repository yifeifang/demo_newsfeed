# Define a dictionary to store the users and their friends
users = {}

# Define a function to create a new user
def create_user(name):
    # Check if the name is valid
    if not name:
        raise ValueError("Name is required")
    # Check if the name already exists
    if name in users:
        raise ValueError("Name already exists")
    # Add the name to the users dictionary with an empty set of friends
    users[name] = set()

# Define a function to get all the users
def get_users():
    # Return the list of user names
    return list(users.keys())

# Define a function to get the friends of a user
def get_friends(name):
    # Check if the user exists
    if name not in users:
        raise ValueError("User not found")
    # Return the list of friend names
    return list(users[name])

# Define a function to add a friend to a user
def add_friend(name, friend):
    # Check if the user exists
    if name not in users:
        raise ValueError("User not found")
    # Check if the friend exists
    if friend not in users:
        raise ValueError("Friend not found")
    # Check if the user and friend are already friends
    if friend in users[name]:
        raise ValueError("Already friends")
    # Add the friend to the user's friends set and vice versa
    users[name].add(friend)
    users[friend].add(name)
