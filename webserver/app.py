from flask import Flask, render_template, request, redirect, session
from requests import get

app = Flask(__name__)
app.secret_key = "very-secret"

username = "admin"
password = "admin"


@app.route("/")
def home():
    if "user" in session:
        user = session["user"]
        return render_template("home.html", username=user)
    else:
        return redirect("/login")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/auth", methods=["POST"])
def auth():
    if request.form["username"] == username and request.form["password"] == password:
        session["user"] = username
        return redirect("/")
    else:
        return redirect("/login")




app.run(debug=False, host="0.0.0.0")
