import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

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
db = SQL("sqlite:///data.db")
@app.route("/")
@login_required
def index():
    return render_template("about.html")



@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    id = session["user_id"]
    role = db.execute("SELECT role FROM users WHERE id = :id", id = id)[0]['role']
    if role == 'guest':
        citas = db.execute("SELECT calendar.day, calendar.hour, users.username, users.role FROM calendar JOIN users ON calendar.id = users.id WHERE user = :id", 
                           id = id)
        memberId = db.execute("SELECT id FROM calendar WHERE user = :id", id = id)
        datos = db.execute("SELECT * FROM users WHERE id = :id", id = id)
        return render_template("profileg.html", datos = datos, citas = citas)
    if role == 'host':
        citas = db.execute("SELECT calendar.day, calendar.hour, users.username, users.role FROM calendar JOIN users ON calendar.id = users.id WHERE user = :id", 
                           id = id)        
        datos = db.execute("SELECT * FROM house WHERE id = :id", id = id)
        return render_template("profileh.html", datos = datos, citas = citas)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/agendar", methods = ["GET", "POST"])
@login_required
def agendar():
    if request.method == "POST":
        id = session["user_id"]
        day = request.form.get("day")
        hour = request.form.get("hour")
        idm = request.form.get("idm")
        username = db.execute("SELECT username FROM users WHERE id = :id", id = id)[0]['username']
        state = db.execute("SELECT state FROM calendar WHERE id = :idm AND day = :day AND hour = :hour",
                           idm = idm, day = day, hour = hour)[0]['state']
        if state != 'available':
            return apology("That date and hour is unavailable", 403)
        db.execute("UPDATE calendar SET state = :state, user = :user, username = :username WHERE id = :idm AND day = :day AND hour = :hour", 
                   state = 'unavailable', user = id, username = username, idm = idm, day = day, hour = hour)
        return redirect("/profile")
        
        
        
@app.route("/psy", methods = ["GET", "POST"])
@login_required
def psy():
    psychologists = db.execute("SELECT * FROM users WHERE role = :role", role = 'psychologist')
    if request.method == "GET":
        return render_template("psys.html", psychologists = psychologists)
    else:
        id = session["user_id"]
        psycho = request.form.get("psycho")
        idp = db.execute("SELECT id FROM users WHERE username = :username", username = psycho)[0]['id']
        calendar = db.execute("SELECT * FROM calendar WHERE id = :id ORDER BY number", id = idp)
        hours = ["7-9am","9-11am","11-1pm","2-4pm","4-6pm","6-8pm"]
        days = ["Monday", "Tuesday","Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return render_template("psy.html", calendar = calendar, hours = hours, days = days)



@app.route("/legal", methods = ["GET", "POST"])
@login_required
def legal():
    lawyers = db.execute("SELECT * FROM users WHERE role = :role", role = 'lawyer')
    if request.method == "GET":
        return render_template("legals.html",lawyers = lawyers)
    else:
        id = session["user_id"]
        lawyer = request.form.get("lawyer")
        idl = db.execute("SELECT id FROM users WHERE username = :username", username = lawyer)[0]['id']
        calendar = db.execute("SELECT * FROM calendar WHERE id = :id ORDER BY number", id = idl)
        hours = ["7-9am","9-11am","11-1pm","2-4pm","4-6pm","6-8pm"]
        days = ["Monday", "Tuesday","Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return render_template("legal.html", calendar = calendar, hours = hours, days = days)
        
        

@app.route("/calendarios")
@login_required
def calendarios():
    db.execute("CREATE TABLE IF NOT EXISTS 'calendar' ('id' INTEGER,'number' INTEGER, 'day' TEXT, 'hour' TEXT, 'state' TEXT, 'user' INTEGER, 'username' TEXT)")
    #se seleccionan las personas que son psicologas o abogadas  
    members = db.execute("SELECT id FROM users WHERE role = 'psychologist' or role = 'lawyer'") 
    calendario = db.execute("SELECT * FROM calendar")
    days = ["Monday", "Tuesday","Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hours = ["7-9am","9-11am","11-1pm","2-4pm","4-6pm","6-8pm"]
    #aqui se llenan los calendarios
    if not calendario:
        for member in members:
            id = member['id']
            j = -1
            for i in range(42):
                day = days[i%7]
                if i%7 == 0:
                    j = j + 1
                hour = hours[j]
                db.execute("INSERT INTO calendar (id, number, day, hour, state, user, username) VALUES (:id, :number, :day, :hour, :state, :user, :username)",
                id = id , number = i + 1, day = day, hour = hour, state = 'available', user = 0 ,username = 'N')
    iduser = session["user_id"]
    roleuser = db.execute("SELECT role FROM users WHERE id = :id", id = iduser)[0]['role']
    if roleuser == 'guest':  
        return render_template("atenciong.html")
    if roleuser == 'host':
        return render_template("atencionh.html")
    else:
        calendar = db.execute("SELECT * FROM calendar WHERE id = :id ORDER BY number", id = iduser)
        hours = ["7-9am","9-11am","11-1pm","2-4pm","4-6pm","6-8pm"]
        days = ["Monday", "Tuesday","Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return render_template("mycalendar.html", calendar = calendar, hours = hours, days = days)



@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "GET":
        return render_template("search.html")
    else:
        department = request.form.get("department").capitalize()
        city = request.form.get("city").capitalize()
        nadult = request.form.get("nadult")
        nchildren = request.form.get("nchildren")
        
        if department == '' or city == '' or nadult == '' or nchildren == '':
            datos = db.execute("SELECT * FROM house WHERE department = :department OR city = :city OR nchildren = :nchildren OR nadult = :nadult",
                           department = department, city = city, nchildren = nchildren, nadult = nadult)
        else:
            datos = db.execute("SELECT * FROM house WHERE department = :department AND city = :city AND nchildren = :nchildren AND nadult = :nadult",
                           department = department, city = city, nchildren = nchildren, nadult = nadult)
        return render_template("search.html", datos = datos)

@app.route("/changeE", methods=["GET", "POST"])
@login_required
def changeE():
    id = session["user_id"]
    if request.method == "GET":
        return render_template("email.html")
    else:
        passwordV = request.form.get("passwordV")
        emailN = request.form.get("emailN")
        hashV = db.execute("SELECT hash FROM users WHERE id = :id", id = id)[0]['hash']
        if not check_password_hash(hashV, passwordV):
            return apology("Your actual password is incorrect", 403)
        db.execute("UPDATE house SET email = :email WHERE id = :id", email = emailN, id = id)
        return redirect("/")

@app.route("/changep", methods=["GET", "POST"])
@login_required
def changep():
    id = session["user_id"]
    if request.method == "GET":
        return render_template("password.html")
    else:
        passwordV = request.form.get("passwordV")
        passwordN = request.form.get("passwordN")
        confirmation = request.form.get("confirmation")
        hashV = db.execute("SELECT hash FROM users WHERE id = :id", id = id)[0]['hash']
        if not check_password_hash(hashV, passwordV):
            return apology("Your actual password is incorrect", 403)
        if passwordN != confirmation:
            return apology("Your new password and confirmation don't match", 403)
        hash1 = generate_password_hash(passwordN)
        db.execute("UPDATE users SET hash = :hash WHERE id = :id", hash = hash1, id = id)
        return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    db.execute("CREATE TABLE IF NOT EXISTS 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL, 'role' TEXT NOT NULL )")
    db.execute("CREATE TABLE IF NOT EXISTS 'guest' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL )")
    db.execute("CREATE TABLE IF NOT EXISTS 'host' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL)")
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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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

    
@app.route("/registerH", methods=["GET", "POST"])
def registerH():
    db.execute("CREATE TABLE IF NOT EXISTS 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL, 'role' TEXT NOT NULL )")
    db.execute("CREATE TABLE IF NOT EXISTS 'guest' ('id' INTEGER, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL )")
    db.execute("CREATE TABLE IF NOT EXISTS 'host' ('id' INTEGER, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS 'house' ('id' INTEGER, 'department' TEXT NOT NULL, 'city' TEXT NOT NULL,'nadult' INTEGER, 'nchildren' INTEGER, 'nbedroom' INTEGER, 'nbathroom' INTEGER, 'service' TEXT NOT NULL, 'email' TEXT)")
    if request.method == "GET":
        return render_template("registerHouse.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        department = request.form.get("department").capitalize()
        city = request.form.get("city").capitalize()
        nadult = request.form.get("nadult")
        nchildren = request.form.get("nchildren")
        nbedroom = request.form.get("nbedroom")
        nbathroom = request.form.get("nbathroom")
        service = request.form.get("service").capitalize()
        email = request.form.get("email")
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username = request.form.get("username"))
        if len(rows) == 1:
            return apology("The username is fill", 403)
        if password != confirmation:
            return apology("You password and confirmation don't match", 403)
        hash1 = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash, role) VALUES (:username, :hash, :role)", username = username , hash = hash1, role = 'host')
        id = int(db.execute("SELECT id FROM users WHERE username = :username", username = username)[0]['id'])
        db.execute("INSERT INTO host (id, username, hash) VALUES (:id, :username, :hash)", username = username , hash = hash1, id = id)
        db.execute("INSERT INTO house (id, department, city, nadult, nchildren, nbedroom, nbathroom, service, email) VALUES (:id, :department, :city, :nadult, :nchildren, :nbedroom, :nbathroom, :service, :email)",
                   id = id, department = department, city = city, nadult = nadult, nchildren = nchildren, nbedroom = nbedroom, nbathroom = nbathroom, service = service, email = email)
        return redirect("/")
        

@app.route("/register", methods=["GET", "POST"])
def register():
    db.execute("CREATE TABLE IF NOT EXISTS 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL, 'role' TEXT NOT NULL )")
    db.execute("CREATE TABLE IF NOT EXISTS 'guest' ('id' INTEGER, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL )")
    db.execute("CREATE TABLE IF NOT EXISTS 'host' ('id' INTEGER, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL)")
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        if not username:
            return apology("You must provide a name", 403)
        password = request.form.get("password")
        if not password:
            return apology("You must provide a password", 403)
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("You must provide a confirmation", 403)
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username = request.form.get("username"))
        if len(rows) == 1:
            return apology("The username is fill", 403)
        if password != confirmation:
            return apology("You password and confirmation don't match", 403)
        hash1 = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash, role) VALUES (:username, :hash, :role)", username = username , hash = hash1, role = 'guest')
        id = int(db.execute("SELECT id FROM users WHERE username = :username", username = username)[0]['id'])
        db.execute("INSERT INTO guest (id, username, hash) VALUES (:id, :username, :hash)", username = username , hash = hash1, id = id)
        return redirect("/")
        
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
