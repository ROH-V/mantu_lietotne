import os
import sqlite3
from flask import Flask, render_template, session, redirect, url_for, request
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "cookie_data"

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def db_connection():
    conn = sqlite3.connect("mantubaze.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    db = db_connection()
    # Pievienots ORDER BY, lai jaunākie atradumi būtu saraksta augšā
    mantubaze = db.execute("SELECT * FROM mantubaze WHERE ivn=1 ORDER BY id DESC").fetchall()
    db.close()
    return render_template("index.html", mantubaze=mantubaze)

@app.route("/deregister", methods=["POST"])
def deregister():
    item_id = request.form.get("id")
    vards = request.form.get("lietotajs")

    if item_id and vards:
        pasreizejais_laiks = datetime.now().strftime("%d.%m.%Y %H:%M")
        db = db_connection()
        db.execute("UPDATE mantubaze SET ivn = 0, p_liet = ?, p_laiks = ? WHERE id = ?",
                   (vards, pasreizejais_laiks, item_id))
        db.commit()
        db.close()
    return redirect(url_for("index"))

@app.route("/arhivs")
def arhivs():
    db = db_connection()
    arhiva_dati = db.execute("SELECT id, p_laiks, attels FROM mantubaze WHERE ivn=0").fetchall()
    pasreizejais_laiks = datetime.now()
    divas_nedelas = timedelta(weeks=2)

    for r in arhiva_dati:
        if r['p_laiks']:
            try:
                pieteiksanas_datums = datetime.strptime(r['p_laiks'], "%d.%m.%Y %H:%M")
                if pasreizejais_laiks - pieteiksanas_datums > divas_nedelas:
                    if r['attels']:
                        cels = os.path.join(app.config['UPLOAD_FOLDER'], r['attels'])
                        if os.path.exists(cels):
                            os.remove(cels)
                    db.execute("DELETE FROM mantubaze WHERE id = ?", (r['id'],))
            except ValueError:
                continue
    db.commit()

    mantubaze = db.execute("SELECT * FROM mantubaze WHERE ivn=0 ORDER BY p_laiks DESC").fetchall()
    db.close()
    return render_template("arhivs.html", mantubaze=mantubaze)

@app.route("/delete_item", methods=["POST"])
def delete_item():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    item_id = request.form.get("id")
    if item_id:
        db = db_connection()
        r = db.execute("SELECT attels FROM mantubaze WHERE id = ?", (item_id,)).fetchone()
        if r and r['attels']:
            cels = os.path.join(app.config['UPLOAD_FOLDER'], r['attels'])
            if os.path.exists(cels):
                os.remove(cels)

        db.execute("DELETE FROM mantubaze WHERE id = ?", (item_id,))
        db.commit()
        db.close()
    return redirect(url_for("arhivs"))

@app.route("/cancel_request", methods=["POST"])
def cancel_request():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    item_id = request.form.get("id")
    if item_id:
        db = db_connection()
        db.execute("UPDATE mantubaze SET ivn = 1, p_liet = NULL, p_laiks = NULL WHERE id = ?", (item_id,))
        db.commit()
        db.close()
    return redirect(url_for("arhivs"))

@app.route("/konts", methods=["GET", "POST"])
def konts():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    message = None
    if request.method == "POST":
        nosaukums = request.form.get("nosaukums")
        apraksts = request.form.get("apraksts")
        kur_atrasts = request.form.get("kur_atrasts")
        k_atrasts = request.form.get("k_atrasts")
        file = request.files.get("manta")

        if not all([nosaukums, apraksts, kur_atrasts, k_atrasts]):
            message = "Kļūda: Visi lauki ir obligāti!"
        else:
            filename = None
            if file and file.filename != '':
                # Pievienojam timestamp, lai failu nosaukumi nedublētos
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S_")
                filename = timestamp + secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            db = db_connection()
            db.execute("""
                INSERT INTO mantubaze
                (nosaukums, apraksts, atrasanas_vieta, laiks, ivn, attels, p_liet, p_laiks)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """, (nosaukums, apraksts, kur_atrasts, k_atrasts, 1, filename, None, None))
            db.commit()
            db.close()
            return redirect(url_for("index"))

    return render_template("konts.html", message=message)

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
