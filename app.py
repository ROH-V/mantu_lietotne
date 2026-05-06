from flask import Flask, render_template, request
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