import os
import uuid

from Notifications import Notifications
from flask import Flask, session, render_template, request, redirect, jsonify
from cs50 import SQL

from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology

# Configure application
app = Flask(__name__)
app.secret_key = 'llavenicocifrada'


# Configure database
db = SQL('sqlite:///bogobike.db')

# Notifications x user
allnotifications = Notifications()


if __name__ == '__main__':
    # app.run(ssl_context='adhoc')
    app.run()

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/map")
def map():
    shops = db.execute('SELECT * FROM shops')
    return render_template("map.html", shops=shops)


@app.route("/")
@login_required
def index():
    # User's id
    # userId = session['user_id']
    # Query user's info
    # userInfo = db.execute('SELECT * FROM users WHERE id = :userId', userId=userId)
    shops = db.execute('SELECT * FROM shops')
    return render_template("index.html", shops=shops)   # userInfo=userInfo)


# Log user in
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':

        # Ensure username was submitted
        if not request.form.get('username'):
            return apology('must provide username', 403)

        # Ensure password was submitted
        elif not request.form.get('password'):
            return apology('must provide password', 403)

        # Query database for username
        rows = db.execute('SELECT * FROM users WHERE username = :username', username=request.form.get('username'))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]['hash'], request.form.get('password')):
            return apology('invalid username and/or password', 403)

        # Remember which user has logged in
        session['user_id'] = rows[0]['id']

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('login.html')


# Logout
@app.route('/logout')
def logout():
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect('/')


# Register User
@app.route('/register', methods=['GET', 'POST'])
def register():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':

        # Ensure username isn't empty
        if not request.form.get('username'):
            return apology('must provide username', 400)

        # Ensure name isn't empty
        if not request.form.get('name'):
            return apology('must provide name', 400)

        # Ensure city isn't empty
        if not request.form.get('city'):
            return apology('must provide city', 400)

        # Ensure mail isn't empty
        if not request.form.get('mail'):
            return apology('must provide mail', 400)

        # Ensure password isn't empty
        elif not request.form.get('password'):
            return apology('must provide password', 400)

        # Ensure confirmation password isn't empty
        elif not request.form.get('confirmation'):
            return apology('must provide confirmation password', 400)

        # Ensure passwords match
        elif request.form.get('password') != request.form.get('confirmation'):
            return apology('passwords do not match', 400)

        name = request.form.get('name')
        city = request.form.get('city').capitalize()
        mail = request.form.get('mail')
        username = request.form.get('username')
        hashed = generate_password_hash(request.form.get('password'))
        latitude = 4.680719
        longitude = -74.084726

        # Insert the user in de db generating a hashed password
        result = db.execute('INSERT INTO users(name, city, mail, username, hash, latitude, longitude) VALUES (:name, :city, :mail, :username, :hashed, :latitude, :longitude)',
                            name=name, city=city, mail=mail, username=username, hashed=hashed, latitude=latitude, longitude=longitude)

        # If the user is already in the db then apology
        if not result:
            return apology('username already exists', 400)

        rows = db.execute('SELECT * FROM users WHERE username = :username', username=request.form.get('username'))

        # Remember which user has logged in
        session['user_id'] = rows[0]['id']

        # Add user to notifications dict
        allnotifications.addUser(rows[0]['id'])

        # Redirect user to home page
        return redirect('/')

    return render_template('register.html')


# Return true if username is available, else false, in JSON format
@app.route('/checkUsername', methods=['GET'])
def checkUsername():
    if request.method == 'GET':

        username = request.args.get('username')
        if len(username) < 1:
            return apology('must provide username', 403)

        user = db.execute('SELECT * FROM users WHERE username = :username', username=username)

        # Check if it's a valid user
        if len(user) == 0:
            return jsonify(True)
        else:
            return jsonify(False)

# Show shops
@app.route('/shop', methods=['GET', 'POST'])
@login_required
def shop():
    # User's id
    userId = session['user_id']
    shops = db.execute('SELECT * FROM shops')
    return render_template('shop.html', shops=shops)


# Send notifications
@app.route('/notify', methods=['GET', 'POST'])
@login_required
def notify():
    # User's id
    userId = session['user_id']
    userInfo = db.execute('SELECT * FROM users WHERE id = :userId', userId=userId)
    infoNotif = {'userId': userId, 'latitude': userInfo[0]['latitude'], 'longitude': userInfo[0]['longitude']}

    if request.method == 'POST':

        notification = request.form.get('notify')
        possibleNotif = ['Stranded', 'Robbed', 'Road Being Repaired', 'Crash', 'Roadblock']

        if notification in possibleNotif:
            infoNotif['notification'] = notification
            infoNotif['notificationId'] = str(uuid.uuid4())
        else:
            return apology('Notification is not valid', 400)

        allnotifications.addNotificationToList(userId, infoNotif)

    return render_template('notify.html')


# Check if there's any notification to show
@app.route('/checkNotif', methods=['GET'])
@login_required
def checkNotif():
    # User's id
    userId = session['user_id']
    if allnotifications.checkIfEmpty(userId):
        return jsonify(False)

    else:
        informationList = allnotifications.getInformationListForUser(userId)
        if informationList:
            return jsonify(informationList)
        else:
            return jsonify(False), 404


# Remove notifications from user list
@app.route('/removeNotif', methods=['POST'])
@login_required
def removeNotif():
    # User's id
    userId = session['user_id']
    notificationIdParam = request.form.get('notificationId')
    allnotifications.deleteNotificationFromUserList(notificationIdParam, userId)
    return jsonify(True), 200
