# Configure application
from flask import Flask, session, render_template
from cs50 import SQL

app = Flask(__name__)
app.secret_key = 'llave'

# Configure database
db = SQL('sqlite:///bogobike.db')


@app.route('/')
def index():
    # User's id
    userId = session['user_id']
    # Query user's info
    userInfo = db.execute('SELECT * FROM users WHERE id = :userId', userId=userId)
    return render_template("index.html", userInfo=userInfo)


if __name__ == '__main__':
    app.run(ssl_context='adhoc')
