import sqlite3

# Conectar ou criar o banco de dados
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Tabela de usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    foto TEXT NULL,
    sobrenome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL
);
""")

# Tabela de pontos turísticos (somente IDs, os dados vêm do CSV)
cursor.execute("""
CREATE TABLE IF NOT EXISTS pontos_turisticos (
    id INTEGER PRIMARY KEY
);
""")

# Tabela de avaliações
cursor.execute("""
CREATE TABLE IF NOT EXISTS avaliacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    ponto_turistico_id INTEGER NOT NULL,
    nota INTEGER CHECK(nota >= 1 AND nota <= 5),
    data_avaliacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (ponto_turistico_id) REFERENCES pontos_turisticos(id)
);
""")

# Tabela de comentários
cursor.execute("""
CREATE TABLE IF NOT EXISTS comentarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    ponto_turistico_id INTEGER NOT NULL,
    texto TEXT NOT NULL,
    data_comentario DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (ponto_turistico_id) REFERENCES pontos_turisticos(id)
);
""")

# Tabela de roteiros
cursor.execute("""
CREATE TABLE IF NOT EXISTS roteiros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    ponto_turistico_id INTEGER NOT NULL,
    hora_inicio TEXT NOT NULL,
    hora_fim TEXT NOT NULL,
    num_adultos INTEGER DEFAULT 0,
    num_idosos INTEGER DEFAULT 0,
    num_criancas INTEGER DEFAULT 0,
    data_roteiro DATE NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (ponto_turistico_id) REFERENCES pontos_turisticos(id)
);
""")

# Salvar e fechar a conexão
conn.commit()
conn.close()

print("Banco de dados criado com sucesso!")
