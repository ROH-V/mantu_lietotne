from flask import Flask, render_template, session, redirect, url_for, request
app = Flask(__name__)
import sqlite3

def db_connection():
    conn = sqlite3.connect("mantubaze.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    db = db_connection()
    mantubaze = db.execute("SELECT * FROM mantubaze WHERE ivn=1").fetchall()
    db.close()
    return render_template("index.html",mantubaze=mantubaze)

def deregister():
    id = request.form.get("id")
    if id:
        db = db_connection()
        db.execute("DELETE FROM registrants WHERE id=?",(id,))
        db.commit()
        db.close()
    #confirmed
    db = db_connection()
    mantubaze = db.execute("SELECT * FROM mantubaze WHERE ivn = 1").fetchall()
    db.close()
    return render_template("index.html",mantubaze=mantubaze)

@app.route("/arhivs")
def arhivs():
    db = db_connection()
    mantubaze = db.execute("SELECT * FROM mantubaze WHERE ivn=0").fetchall()
    db.close()
    return render_template("arhivs.html",mantubaze=mantubaze)

app.secret_key = "cookie_data"


@app.route("/konts", methods=["POST"])
def register():
    #validation
    nosaukums = request.form.get("nosaukums")
    if not nosaukums:
        return render_template("konts.html",message=" error")
    
    apraksts = request.form.get("apraksts")
    if not apraksts:
        return render_template("konts.html",message=" error")
    
    kur_atrasts = request.form.get("kur_atrasts")
    if not kur_atrasts:
        return render_template("konts.html",message=" error")
    
    k_atrasts = request.form.get("k_atrasts")
    if not k_atrasts:
        return render_template("konts.html",message=" error")

    db = db_connection()
    db.execute("INSERT INTO mantubaze (nosaukums,apraksts, atrasanas_vieta, laiks, ivn) VALUES(?, ?, ?, ?, ?)", (nosaukums, apraksts, kur_atrasts, k_atrasts,1))
    db.commit()
    db.close()

    #confirmed
    db = db_connection()
    mantubaze = db.execute("SELECT * FROM mantubaze WHERE ivn = 1").fetchall()
    db.close()
    return render_template("index.html",mantubaze=mantubaze)

#################################
@app.route("/konts")
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



#pythonanywhere