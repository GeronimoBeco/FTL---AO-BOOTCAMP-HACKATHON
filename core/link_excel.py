import core.entidades as entity
import sqlite3
from core.entidades import Entity
import pandas as pd

EXCEL_DATA_PATH = entity.data_path + "/data/pontos_turisticos.xlsx"
ENGINE = 'openpyxl'

def fill_tourist_attraction_table():
    """
    Função que serve para preencher a tabela pontos turisticos com os dados de excel
    É muito mais aconselhado usar esta função manualmente.
    """

    df = pd.read_excel(EXCEL_DATA_PATH, engine=ENGINE)
    for index, row in df.iterrows():
        entity.TouristAttraction(row["ID"]).save()

def listar_pontos_turisticos_mais_avaliados(limit=None):
    conn = Entity.get_connection()
    cursor = conn.cursor()

    query = '''
        SELECT
            pontos_turisticos.id,
            COUNT(avaliacoes.id) AS total_avaliacoes,
            ROUND(AVG(avaliacoes.nota), 2) AS media_nota
        FROM pontos_turisticos
        JOIN avaliacoes ON pontos_turisticos.id = avaliacoes.ponto_turistico_id
        GROUP BY pontos_turisticos.id
        ORDER BY media_nota DESC
    '''

    if limit:
        query += f' LIMIT {limit}'

    cursor.execute(query)
    resultados = cursor.fetchall()
    conn.close()

    return resultados
