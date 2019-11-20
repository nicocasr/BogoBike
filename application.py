import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
#import flask.ext.session
#from flask_session.__init__ import Session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# New
#from flask_socketio import SocketIO, send

from helpers import apology, login_required, lookup, usd

import requests


# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# New
"""
socketio = SocketIO(app)

@socketio.on("message")
def handleMessage(msg):
    print("Message: " + msg)
    send(msg, broadcast=True)

usersLogged = []
msgNot = []
"""

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///bogobike.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # User's id
    userId = session["user_id"]
    # Query user's info
    userInfo = db.execute("SELECT * FROM users WHERE id = :userId", userId=session["user_id"])
    return render_template("index.html", userInfo=userInfo)


@app.route("/checkUsername", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    if request.method == "GET":

        username = request.args.get("username")
        if len(username) < 1:
            return apology("must provide username", 403)

        user = db.execute("SELECT * FROM users WHERE username = :username", username=username)

        # Check if it's a valid user
        if len(user) == 0:
            return jsonify(True)
        else:
            return jsonify(False)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Session ID
        #usersLogged.append({request.form.get("username") : session["user_id"]})


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username isn't empty
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure name isn't empty
        if not request.form.get("name"):
            return apology("must provide name", 400)

        # Ensure city isn't empty
        if not request.form.get("city"):
            return apology("must provide city", 400)

        # Ensure mail isn't empty
        if not request.form.get("mail"):
            return apology("must provide mail", 400)

        # Ensure password isn't empty
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation password isn't empty
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation password", 400)

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 400)

        name = request.form.get("name")
        city = request.form.get("city").capitalize()
        mail = request.form.get("mail")
        username = request.form.get("username")
        hashed = generate_password_hash(request.form.get("password"))

        #response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyD86jevTtP1vkg95TkY9i7hGA0045N7Fj4&address=" + request.form.get("address"))

        #resp_json_payload = response.json()


        #latitude = resp_json_payload['results'][0]['geometry']['location']['lat']
        #longitude = resp_json_payload['results'][0]['geometry']['location']['lng']

        latitude = 4.680719
        longitude = -74.084726

        # Insert the user in de db generating a hashed password
        result = db.execute("INSERT INTO users(name, city, mail, username, hash, latitude, longitude) VALUES (:name, :city, :mail, :username, :hashed, :latitude, :longitude)",
                            name=name, city=city, mail=mail, username=username, hashed=hashed, latitude=latitude, longitude=longitude)

        # If the user is already in the db then apology
        if not result:
            return apology("username already exists", 400)

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    return render_template("register.html")


@app.route("/shop", methods=["GET", "POST"])
@login_required
def shop():

    # User's id
    userId = session["user_id"]
    shops = db.execute("SELECT * FROM shops")
    return render_template("shop.html",shops=shops)


@app.route("/notify", methods=["GET", "POST"])
@login_required
def notify():

    # User's id
    userId = session["user_id"]

    userInfo = db.execute("SELECT * FROM users WHERE id = :userId", userId=userId)

    latitude = userInfo[0]["latitude"]

    longitude = userInfo[0]["longitude"]

    if request.method == "POST":

        notification = request.form.get("notify")

        possibleNotif = ['Stranded','Robbed','Road Being Repaired','Crash','Roadblock']

        if notification in possibleNotif:
            insert = db.execute("INSERT INTO notifications(notification, userId, latitude, longitude) VALUES (:notification, :userId, :latitude, :longitude)",
                            notification=notification, userId=userId, latitude=latitude, longitude=longitude)
            if not insert:
                return apology("Couldn't send the notification", 400)
        else:
            return apology("Notification isn't valid", 400)
    return render_template("notify.html")


@app.route("/checkNotif", methods=["GET"])
@login_required
def checkNotif():
    # User's id
    userId = session["user_id"]
    notification = db.execute("SELECT * FROM notifications WHERE userId != :userId", userId=userId)
    if not notification:
        return jsonify(False)
    userInfo = db.execute("SELECT * FROM users WHERE id = :userId", userId=userId)
    latitude = str(userInfo[0]['latitude'])
    longitude = str(userInfo[0]['longitude'])

    decimalLatitude = int(latitude.split('.')[1][:4])
    decimalLongitude = int(longitude.split('.')[1][:4])

    result = []

    for i in range(len(notification)):

        latitude2 = str(notification[i]['latitude'])
        longitude2 = str(notification[i]['longitude'])
        decimalLatitude2 = int(latitude2.split('.')[1][:4])
        decimalLongitude2 = int(longitude2.split('.')[1][:4])
        if abs(decimalLatitude - decimalLatitude2) <= 400 and abs(decimalLongitude - decimalLongitude2) <= 400:
            result.append(notification[i])
    if len(result) <= 0:
        return jsonify(False)
    else:
        return jsonify(result)


"""
@socketio.on('msg', namespace='/notification')
def recieve_notification(msg):
    msgNot.append({msg : request.sid})
    print(msgNot)
"""


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
