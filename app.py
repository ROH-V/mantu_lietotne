from flask import Flask, render_template, session, redirect, url_for, request
app = Flask(__name__)
import sqlite3

def db_connection():
    conn = sqlite3.connect("datubaze.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")


def registrs():
    db = db_connection()
    registrs = db.execute("SELECT * FROM registrs").fetchall()
    db.close()
    return render_template("pieteicies.html",registrs=registrs)

@app.route("/arhivs.html")
def arhivs():
    return render_template("arhivs.html")

app.secret_key = "cookie_data"

@app.route("/konts.html")
def konts():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    return render_template("konts.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    kluda = None
    if request.method == "POST":
        vards = request.form.get("username")
        parole = request.form.get("password")

        if vards == "OVG_" and parole == "uwu":
            session["logged_in"] = True
            session["user"] = vards
            return redirect(url_for("konts"))
        else:
            kluda = "Nepareizs lietotājvārds vai parole!"

    return render_template("login.html", kluda=kluda)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
