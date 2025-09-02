from flask import Flask, render_template
import sqlite3
import csv

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/csv")
def mostrar_csv():
    dados = []
    with open("data/dados.csv", newline="", encoding="utf-8") as csvfile:
        leitor = csv.reader(csvfile)
        for linha in leitor:
            dados.append(linha)
    return {"dados": dados}

@app.route("/db")
def consultar_db():
    conn = sqlite3.connect("data/database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()
    conn.close()
    return {"tabelas": tabelas}

if __name__ == "__main__":
    app.run(debug=True)
