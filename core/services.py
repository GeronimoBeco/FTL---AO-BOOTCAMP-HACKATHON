import sqlite3
from datetime import datetime
from core.entidades import RoadMap, Entity

DB_PATH = "data/database.db"

# Criar roteiros

def criar_roteiros(user_id: int):

    """Cria um roteiro associado a um usuário logado.
    Retorna True se sucesso, False caso contrário.
    """
    if not user_id:
        print("Faça o login para criar um roteiro.")
        return False

    try:
        ponto_id = int(input("Digite o ID do ponto turístico: "))
    except ValueError:
        print("O ID do ponto turístico deve ser um número inteiro.")
        return False

    data_visita = input("Digite a data de visita (YYYY-MM-DD): ")

    # valida formato da data
    try:
        datetime.strptime(data_visita, "%Y-%m-%d")
    except ValueError:
        print("Data inválida. Use o formato YYYY-MM-DD.")
        return False

    roteiro = RoadMap(
        user_id=user_id,
        tourist_attraction_id=ponto_id,
        start_time="08:00",  
        end_time="18:00",
        road_map_date=data_visita
    )

    if roteiro.save():
        print("Roteiro criado com sucesso!")
        return True
    else:
        print("Erro ao salvar o roteiro.")
        return False



# Destinos mais avaliados
def destinos_mais_avaliados(limit: int = 5):
    
    """Retorna os destinos mais avaliados como lista de dicionários."""
    
    conn = Entity.get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT pt.nome, AVG(av.nota) AS media_avaliacao
        FROM pontos_turisticos pt
        JOIN avaliacoes av ON pt.id = av.ponto_turistico_id
        GROUP BY pt.id
        HAVING COUNT(av.id) > 0
        ORDER BY media_avaliacao DESC
        LIMIT {limit}
    ''')
    rows = cursor.fetchall()
    conn.close()

    resultados = [{"nome": nome, "media": round(media, 2)} for nome, media in rows]

    if resultados:
        print("\nTop Destinos Mais Avaliados:")
        for idx, destino in enumerate(resultados, 1):
            print(f"{idx}. {destino['nome']} | Média: {destino['media']:.2f} ⭐")
    else:
        print("Nenhum dado de avaliação encontrado.")

    return resultados

    


# Pontos turísticos por província
def pontos_turisticos_por_provincias():
    """Retorna pontos turísticos agrupados por província em lista de dicionários."""
    conn = Entity.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT provincia, COUNT(*) AS total_pontos
        FROM pontos_turisticos
        GROUP BY provincia
        ORDER BY total_pontos DESC
    ''')
    rows = cursor.fetchall()
    conn.close()

    resultados = [{"provincia": provincia, "total": total} for provincia, total in rows]

    if resultados:
        print("\n📍 Pontos Turísticos por Província:")
        for item in resultados:
            print(f"- {item['provincia']}: {item['total']} pontos turísticos")
    else:
        print("Nenhum ponto turístico encontrado.")

    return resultados 