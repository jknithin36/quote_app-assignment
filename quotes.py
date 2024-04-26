from flask import Flask, render_template, request, redirect, session
from mongita import MongitaClientDisk
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# create a mongita client connection
client = MongitaClientDisk()

# open the quotes database
quotes_db = client.quotes_db

# Define the valid username
valid_username = "jk"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username == valid_username:
            session['logged_in'] = True
            return redirect("/quotes")
        else:
            return render_template("login.html", message="Invalid username. Please try again.")
    return render_template("login.html")

@app.route("/", methods=["GET"])
@app.route("/quotes", methods=["GET"])
def get_quotes():
    if not session.get('logged_in'):
        return redirect("/login")
    
    # open the quotes collection
    quotes_collection = quotes_db.quotes_collection
    # load the data
    data = list(quotes_collection.find({}))
    for item in data:
        item["_id"] = str(item["_id"])
        item["object"] = ObjectId(item["_id"])
    # display the data
    return render_template("quotes.html", data=data)

@app.route("/add", methods=["GET"])
def get_add():
    if not session.get('logged_in'):
        return redirect("/login")
    return render_template("add_quote.html")

@app.route("/add", methods=["POST"])
def post_add():
    if not session.get('logged_in'):
        return redirect("/login")
    
    text = request.form.get("text", "")
    author = request.form.get("author", "")
    if text != "" and author != "":
        # open the quotes collection
        quotes_collection = quotes_db.quotes_collection
        # insert the quote
        quote_data = {"text": text, "author": author}
        quotes_collection.insert_one(quote_data)
    return redirect("/quotes")

@app.route("/edit/<id>", methods=["GET"])
def get_edit(id=None):
    if not session.get('logged_in'):
        return redirect("/login")
    
    if id:
        # open the quotes collection
        quotes_collection = quotes_db.quotes_collection
        # get the item
        data = quotes_collection.find_one({"_id": ObjectId(id)})
        data["id"] = str(data["_id"])
        return render_template("edit_quote.html", data=data)
    return redirect("/quotes")

@app.route("/edit", methods=["POST"])
def post_edit():
    if not session.get('logged_in'):
        return redirect("/login")
    
    _id = request.form.get("_id", None)
    text = request.form.get("text", "")
    author = request.form.get("author", "")
    if _id:
        # open the quotes collection
        quotes_collection = quotes_db.quotes_collection
        # update the values in this particular record
        values = {"$set": {"text": text, "author": author}}
        data = quotes_collection.update_one({"_id": ObjectId(_id)}, values)
    return redirect("/quotes")

@app.route("/delete", methods=["GET"])
@app.route("/delete/<id>", methods=["GET"])
def get_delete(id=None):
    if not session.get('logged_in'):
        return redirect("/login")
    
    if id:
        # open the quotes collection
        quotes_collection = quotes_db.quotes_collection
        # delete the item
        quotes_collection.delete_one({"_id": ObjectId(id)})
    return redirect("/quotes")

if __name__ == "__main__":
    app.run(debug=True)