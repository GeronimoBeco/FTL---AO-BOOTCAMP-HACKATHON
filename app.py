from flask import Flask, render_template, request, redirect, url_for, session, flash
from core.entidades import User  # Certifique-se que está importando corretamente
import os
import geopandas as gpd
import folium
import sqlite3
import csv
import pandas as pd
from core.entidades import Avaliation
from datetime import datetime
from core.entidades import RoadMap


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Para proteger as sessions
EXCEL_PATH = os.path.join(os.getcwd(), 'data', 'pontos_turisticos.xlsx')
DB_PATH = os.path.join(os.getcwd(), 'data', 'database.db')


@app.before_request
def proteger_rotas():
    rotas_livres = ['login', 'cadastro', 'static']  # rotas livres
    if 'usuario' not in session and request.endpoint not in rotas_livres:
        return redirect(url_for('login'))

# Obter os 7 pontos mais bem avaliados (do banco de dados)
def get_top_rated_ids(limit=7):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
        SELECT ponto_turistico_id, ROUND(AVG(nota), 2) as media
        FROM avaliacoes
        GROUP BY ponto_turistico_id
        ORDER BY media DESC
        LIMIT ?
    '''
    cursor.execute(query, (limit,))
    result = cursor.fetchall()
    conn.close()

    # Retorna lista de IDs em ordem de média
    return [row[0] for row in result]

# Carrega os dados do Excel e filtra os que estão nos IDs top avaliados
def get_top_rated_spots():
    df = pd.read_excel(EXCEL_PATH, engine='openpyxl')

    top_ids = get_top_rated_ids()

    # Filtra os pontos turísticos cujos IDs estão nos mais avaliados
    filtered_df = df[df['ID'].isin(top_ids)]

    # Garante que a ordem no DataFrame seja igual à ordem dos top_ids
    filtered_df['ID'] = pd.Categorical(filtered_df['ID'], categories=top_ids, ordered=True)
    filtered_df = filtered_df.sort_values('ID')

    # Converte para lista de dicionários
    pontos = []
    for _, row in filtered_df.iterrows():
        pontos.append({
            'id': row['ID'],
            'nome': row['Nome'],
            'url_imagem': row['URL_Imagem']
        })

    return pontos

@app.route("/")
def home():
    pontos = get_top_rated_spots()
    return render_template("home.html", pontos_turisticos=pontos)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = sqlite3.connect("data/database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["usuario"] = {"id": user[0], "nome": user[1]}
            return redirect(url_for("home"))
        else:
            error = "Email ou senha incorretos"
            return render_template("login.html", error=error)

    return render_template("login.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        sobrenome = request.form["sobrenome"]
        email = request.form["email"]
        senha = request.form["senha"]

        novo_usuario = User(name=nome, lastname=sobrenome, email=email, password=senha)
        novo_usuario.save()

        flash("Usuário cadastrado com sucesso! Faça login.")
        return redirect(url_for("login"))

    return render_template("cadastro.html")

@app.route('/ponto_turistico/<int:ponto_id>')
def ponto_turistico(ponto_id):
    # Carrega todos os dados do Excel
    df = pd.read_excel(EXCEL_PATH, engine='openpyxl')
    row = df[df['ID'] == ponto_id].iloc[0]

    ponto = {
        'id': row['ID'],
        'nome': row['Nome'],
        'latitude': row['Latitude'],
        'longitude': row['Longitude'],
        'provincia': row['Provincia'],
        'municipio': row['Municipio'],
        'descricao': row['Descrição'],
        'horario': row['Horário'],
        'precario': row['Preçário'],
        'url_imagem': row['URL_Imagem']
    }

    # Buscar média da avaliação no banco
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ROUND(AVG(nota), 1)
        FROM avaliacoes
        WHERE ponto_turistico_id = ?
    ''', (ponto_id,))
    media = cursor.fetchone()[0]
    conn.close()

    ponto['media_avaliacao'] = media if media is not None else 0.0

    # Verifica se o usuário avaliou esse ponto
    avaliacao_usuario = 0
    if "usuario" in session:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nota FROM avaliacoes
            WHERE usuario_id = ? AND ponto_turistico_id = ?
        ''', (session["usuario"]["id"], ponto_id))
        resultado = cursor.fetchone()
        if resultado:
            avaliacao_usuario = int(resultado[0])
        conn.close()

    return render_template('ponto_turistico.html', ponto=ponto, avaliacao_usuario=avaliacao_usuario)

from core.entidades import Avaliation
from flask import jsonify

@app.route('/avaliar', methods=['POST'])
def avaliar():
    if 'usuario' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

    data = request.get_json()
    user_id = session['usuario']['id']
    ponto_id = data.get('ponto_id')
    nota = data.get('nota')

    if not ponto_id or not nota:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400

    # Verificar se já existe avaliação
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM avaliacoes
        WHERE usuario_id = ? AND ponto_turistico_id = ?
    ''', (user_id, ponto_id))
    row = cursor.fetchone()
    conn.close()

    if row:
        avaliacao = Avaliation(user_id, ponto_id, nota, id=row[0])
    else:
        avaliacao = Avaliation(user_id, ponto_id, nota)

    avaliacao.save()

    return jsonify({'success': True, 'message': 'Avaliação salva com sucesso'})

@app.route("/criar-roteiro/<int:ponto_id>", methods=["GET"])
def criar_roteiro(ponto_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    # Carrega os dados do ponto turístico do Excel
    df = pd.read_excel(EXCEL_PATH, engine='openpyxl')
    row = df[df['ID'] == ponto_id].iloc[0]

    ponto = {
        'id': int(row['ID']),
        'nome': row['Nome']
    }

    return render_template("criar_roteiro.html", ponto=ponto)

from core.entidades import RoadMap
from flask import request, redirect, url_for, session, flash

@app.route('/salvar-roteiro', methods=['POST'])
def salvar_roteiro():
    if 'usuario' not in session:
        flash("Você precisa estar logado para criar um roteiro.")
        return redirect(url_for('login'))

    user_id = session['usuario']['id']
    ponto_id = int(request.form.get('ponto_id'))
    chegada = request.form.get('chegada')
    saida = request.form.get('saida')
    adultos = int(request.form.get('adultos', 0))
    criancas = int(request.form.get('criancas', 0))
    idosos = int(request.form.get('idosos', 0))

    # Validar datas (pode melhorar isso)
    if chegada >= saida:
        flash("A data/hora de chegada deve ser anterior à de saída.")
        return redirect(url_for('criar_roteiro', ponto_id=ponto_id))

    # Criar o roteiro
    roteiro = RoadMap(
        user_id=user_id,
        tourist_attraction_id=ponto_id,
        start_time=chegada,
        end_time=saida,
        num_adulto=adultos,
        num_criancas=criancas,
        num_idoso=idosos
    )
    roteiro.save()

    flash("Roteiro salvo com sucesso!")
    return redirect(url_for('roteiro'))

@app.route('/roteiro')
def roteiros():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    user_id = session['usuario']['id']
    # Busca roteiros do usuário
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, ponto_turistico_id, hora_inicio, hora_fim, num_adultos, num_idosos, num_criancas, data_roteiro
        FROM roteiros
        WHERE usuario_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()

    # Carrega dados dos pontos turísticos
    df = pd.read_excel(EXCEL_PATH, engine='openpyxl')

    agora = datetime.now()

    em_andamento = []
    finalizados = []

    for row in rows:
        id_rm, ponto_id, hora_inicio_str, hora_fim_str, adultos, idosos, criancas, data_roteiro = row
        hora_inicio = datetime.fromisoformat(hora_inicio_str)
        hora_fim = datetime.fromisoformat(hora_fim_str)

        ponto_row = df[df['ID'] == ponto_id].iloc[0]
        ponto_data = {
            'roteiro_id': id_rm,
            'ponto_id': ponto_id,
            'nome': ponto_row['Nome'],
            'url_imagem': ponto_row['URL_Imagem'],
            'hora_inicio': hora_inicio,
            'hora_fim': hora_fim,
            'num_adultos': adultos,
            'num_idosos': idosos,
            'num_criancas': criancas,
        }

        if hora_inicio < agora:
            finalizados.append(ponto_data)
        else:
            em_andamento.append(ponto_data)

    return render_template('roteiro.html', em_andamento=em_andamento, finalizados=finalizados)


@app.route('/mapa')
def mapa():
    provincias = gpd.read_file("data/geoBoundaries-AGO-ADM1.geojson")
    df_pontos = pd.read_excel(EXCEL_PATH, engine='openpyxl')
    
    provincias_com_pontos = df_pontos['Provincia'].dropna().unique()
    provincias_com_pontos = [p.lower() for p in provincias_com_pontos]

    mapa = folium.Map(location=[-11.2027, 17.8739], zoom_start=6)
    folium.GeoJson(
        provincias,
        name="Províncias",
        style_function=lambda x: {
            "fillColor": "#88cc88",
            "color": "green",
            "weight": 1,
            "fillOpacity": 0.3
        },
        tooltip=folium.GeoJsonTooltip(fields=["shapeName"], aliases=["Província:"]),
        popup=folium.GeoJsonPopup(fields=["shapeName"])
    ).add_to(mapa)

    for _, row in provincias.iterrows():
        nome_provincia = row["shapeName"]
        if nome_provincia.lower() not in provincias_com_pontos:
            continue  # Ignora se a província não tem pontos turísticos

        ponto = row.geometry.representative_point()
        link = f"/provincia/{nome_provincia.replace(' ', '_')}"

        folium.Marker(
            location=[ponto.y, ponto.x],
            tooltip=nome_provincia,
            popup=f"<a href='{link}' target='_blank'>Ver pontos turísticos de {nome_provincia}</a>",
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(mapa)

    folium.LayerControl().add_to(mapa)
    mapa_html = mapa._repr_html_()

    return render_template("mapa.html", mapa_html=mapa_html)

@app.route('/provincia/<nome>')
def ver_provincia(nome):
    df = pd.read_excel(EXCEL_PATH, engine='openpyxl')

    # Filtra os pontos turísticos da província
    pontos_df = df[df['Provincia'].str.lower() == nome.replace("_", " ").lower()]

    if pontos_df.empty:
        flash("Nenhum ponto turístico encontrado para esta província.")
        return redirect(url_for('mapa'))

    pontos = []
    for _, row in pontos_df.iterrows():
        pontos.append({
            'id': row['ID'],
            'nome': row['Nome'],
            'url_imagem': row['URL_Imagem'],
            'precario': row['Preçário'],
            'avaliacao': 0.0  # Adicionaremos média depois
        })

    # Buscando avaliações médias
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for ponto in pontos:
        cursor.execute('SELECT ROUND(AVG(nota), 1) FROM avaliacoes WHERE ponto_turistico_id = ?', (ponto['id'],))
        media = cursor.fetchone()[0]
        ponto['avaliacao'] = media if media else 0.0
    conn.close()

    return render_template('provincia.html', provincia=nome.replace("_", " ").title(), pontos=pontos)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
