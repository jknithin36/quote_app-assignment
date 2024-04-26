from flask import Flask, render_template, request, make_response, redirect
from mongita import MongitaClientDisk
from bson import ObjectId

app = Flask(__name__)

# create a mongita client connection
client = MongitaClientDisk()

# open the quotes database
quotes_db = client.quotes_db
session_db = client.session_db
user_db = client.user_db

import uuid

@app.route("/", methods=["GET"])
@app.route("/quotes", methods=["GET"])
def get_quotes():
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        response = redirect("/login")
        return response
    # open the session collection
    session_collection = session_db.session_collection
    # get the data for this session
    session_data = list(session_collection.find({"session_id": session_id}))
    if len(session_data) == 0:
        response = redirect("/logout")
        return response
    assert len(session_data) == 1
    session_data = session_data[0]
    # get some information from the session
    user = session_data.get("user", "unknown user")
    # open the quotes collection
    quotes_collection = quotes_db.quotes_collection
    # load the data
    data = list(quotes_collection.find({"owner":user}))
    for item in data:
        item["_id"] = str(item["_id"])
        item["object"] = ObjectId(item["_id"])
    # display the data
    html = render_template(
        "quotes.html",
        data=data,
        user=user,
    )
    response = make_response(html)
    response.set_cookie("session_id", session_id)
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user", "")
        if user == "jk":  # Only allow login with username "jk"
            session_id = str(uuid.uuid4())
            # open the session collection
            session_collection = session_db.session_collection
            # insert the user
            session_collection.delete_one({"session_id": session_id})
            session_data = {"session_id": session_id, "user": user}
            session_collection.insert_one(session_data)
            response = redirect("/add")  # Redirect to the add quote page
            response.set_cookie("session_id", session_id)
            return response
    return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout():
    session_id = request.cookies.get("session_id", None)
    if session_id:
        # open the session collection
        session_collection = session_db.session_collection
        # delete the session
        session_collection.delete_one({"session_id": session_id})
    response = redirect("/login")
    response.delete_cookie("session_id")
    return response

# Other routes remain unchanged...

if __name__ == "__main__":
    app.run(debug=True)
