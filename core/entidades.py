import os
import sqlite3
from datetime import datetime

data_path = os.getcwd()

os.sep = "/"
class Entity:
    DATA_BASE_PATH = data_path + "/data/database.db" # Enderço da BD
    
    @classmethod
    def get_connection(cls):
        return sqlite3.connect(cls.DATA_BASE_PATH)

class User(Entity): # Usuario
    def __init__(self, name: str, photo: "str|None" = None,
                 lastname: str = '', email: str = '', password: str = '',
                 id: "int|None" = None
                 ):
        self.id = id
        self.name = name
        self.lastname = lastname
        self.photo = photo
        self.email = email
        self.password = password

    def register(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.id == None:
            cursor.execute('''
                INSERT INTO usuarios(nome, sobrenome, email, senha, foto)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.name, self.lastname, self.email, self.password, self.photo))
        else:
            cursor.execute('''
                UPDATE usuarios SET nome=?, sobrenome=?, email=?, senha=?, foto=?)
                WHERE id=?
            ''', (self.name, self.lastname, self.email, self.password, self.photo, self.id))

        conn.commit()
        conn.close()

    def save(self):
        self.register()

    def update(self):
        self.register()
        
    @classmethod
    def search_from_id(cls, user_id: int, show_value: bool=True):
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            if show_value: return row
            else: return cls(*row[1:], id=row[0])
        return None
    

class TouristAttraction(Entity): # Ponto turistico
    def __init__(self, id):
        self.id = id

    def save(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO pontos_turisticos (id) VALUES (?)", (self.id,))
        conn.commit()
        conn.close()

class Avaliation(Entity): # Avaliação
    def __init__(self, user_id, tourist_attraction_id, mark,
                 avaliation_date=None, id=None):
        self.id = id
        self.user_id = user_id
        self.tourist_attraction_id = tourist_attraction_id
        self.mark = mark
        self.avaliation_date = avaliation_date or datetime.now()

    def save(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        print("DEBUG types:")
        print("user_id:", self.user_id, type(self.user_id))
        print("tourist_attraction_id:", self.tourist_attraction_id, type(self.tourist_attraction_id))
        print("mark:", self.mark, type(self.mark))


        if self.id is None:
            cursor.execute('''
                INSERT INTO avaliacoes (usuario_id, ponto_turistico_id, nota)
                VALUES (?, ?, 5)
            ''', (self.user_id, self.tourist_attraction_id))
            self.id = cursor.lastrowid
        else:
            cursor.execute('''
                UPDATE avaliacoes
                SET usuario_id=?, ponto_turistico_id=?, nota=?
                WHERE id=?
            ''', (self.user_id, self.tourist_attraction_id, int(self.mark), self.id))

        conn.commit()
        conn.close()
        
class Comment(Entity): # Comentário
    def __init__(self, user_id, tourist_attraction_id, text, comment_date=None):
        self.user_id = user_id
        self.tourist_attraction_id = tourist_attraction_id
        self.text = text
        self.comment_date = comment_date

    def save(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                INSERT INTO comentarios (usuario_id, ponto_turistico_id, texto, data_comentario)
                VALUES (?, ?, ?, ?)
            ''', (self.user_id, self.tourist_attraction_id, self.text, self.comment_date))
        conn.commit()
        conn.close()

    @classmethod
    def search_from_id(cls, id_comment, show_value: bool=True):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * comentarios WHERE id = ?', (id_comment))
        row = cursor.fetchone()
        conn.close()

        if row:
            if show_value: return row
            else: return cls(*row[1], row[0])
        return None

class RoadMap(Entity): # Roteiro
    def __init__(self, user_id, tourist_attraction_id, start_time, end_time,
                 num_adulto=0, num_idoso=0, num_criancas=0, road_map_date=None, id=None):
        self.id = id
        self.user_id = user_id
        self.tourist_attraction_id = tourist_attraction_id
        self.start_time = start_time
        self.end_time = end_time
        self.num_adulto = num_adulto
        self.num_idoso = num_idoso
        self.num_criancas = num_criancas
        self.road_map_date = road_map_date or datetime.now()
    
    def save(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                INSERT INTO roteiros (
                    usuario_id, ponto_turistico_id, hora_inicio, hora_fim,
                    num_adultos, num_idosos, num_criancas, data_roteiro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.user_id, self.tourist_attraction_id, self.start_time, self.end_time,
                  self.num_adulto, self.num_idoso, self.num_criancas, self.road_map_date))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

        return 1

    def update(self):
        if self.id is None:
            raise ValueError("Introduza um id válido ao roteiro")

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                UPDATE roteiros SET
                    usuario_id = ?,
                    ponto_turistico_id = ?,
                    hora_inicio = ?, hora_fim = ?,
                    num_adulto = ?, num_idosos = ?, num_criancas = ?,
                    data_roteiro = ?
                WHERE id=?
            ''', (self.user_id, self.tourist_attraction_id, self.start_time,
                self.end_time, self.num_adulto, self.num_idoso, self.num_criancas,
                self.road_map_date))
        conn.commit()
        conn.close()

    def delete(self):
        if self.id is None:
            raise ValueError("Introduza um id válido ao roteiro")

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM roteiros WHERE id = ?', (self.id))
        conn.commit()
        conn.close()
        self.id = None

    @classmethod
    def search_from_id(self, id_road_map, show_value: bool=True):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * from roteiros WHERE id = ?', (id_road_map))
        row = cursor.fetchone()
        conn.close()

        if row:
            if show_value: return row
            else: return cls(*row[1], row[0])
        return None
