import core.entidades as entity
import sqlite3, os

entity.data_path = os.getcwd()
def verificar_senha_e_email(email, senha):
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    row = cursor.fetchall()
    for i in row:
        if i[4] == email and i[5] == senha:
            return i[0], i[1], i[3]
    return (0,)
    conn.close()
    
class Program:
    USER_ID = 0
    
    def login(self): #Login
        tentativa = 3
        while 1:
            email = input("Digite o email: ")
            senha = input("Digite a senha: ")
            user_info = verificar_senha_e_email(email, senha)
            
            self.USER_ID = int(user_info[0])
            
            if self.USER_ID:
                print("Seja bem-vindo/a", user_info[1], user_info[2])
                return 1
            
            print("Email ou senha incorreta, tente novamente!")
            tentativa -= 1 
            print("Tentativas restante:", tentativa)
            if not tentativa:
                return 0
            

    def sign_in(self): # Cadastro
        nome = input("Digite o nome: ")
        sobre_nome = input("Digite a sobre nome: ")
        email = input("Digite o email: ")
        senha = input("Digite a senha: ")

        usuario = entity.User(name=nome, lastname=sobre_nome, email=email, password=senha)
        usuario.save()
        print("Dados Salvo")

    def criar_roteiros(self):
        "FALTA A IMPLEMENTAÇÃO DESTE METODO"

    def destinos_mais_avaliados(self):
        "FALTA A IMPLEMENTAÇÃO DESTE METODO"

    def pontos_turisticos_por_provincias(self):
        "FALTA A IMPLEMENTAÇÃO DESTE METODO"
    
def titulo(name):
    print("-"*60)
    print(name.upper().center(60))
    print("-"*60)


if __name__ == "__main__":
    while 1:
        titulo("ROTEIRO INTELIGENTE DE ECOTURISMO")
        print("1) Login")
        print("2) Registrar")
        print("3) Sair")
        op = int(input(":"))
        if op == 1:
            titulo("LOGIN")
            login = Program().login()
            if login: break
        elif op == 2:
            titulo("REGISTRAR")
            Program().sign_in()
        elif op == 3:
            exit()
        
    while 1:
        titulo("MENU PRINCIPAL")
        print("1) Destinos mais Avaliados")
        print("2) Criar novo Roteiro")
        print("3) Pontos turisticos por Província")
        print("5) Sair")
        op = int(input(":"))
        if op == 1:
            titulo("Destinos mais Avaliados")
            print("Aguardando implemetação")
            break
        elif op == 2:
            titulo("Criar novo Roteiro")
            print("Aguardando implemetação")
            break
        elif op == 3:
            titulo("Pontos turisticos por Província")
            print("Aguardando implemetação")
            break
        elif op == 5:
            exit()
        
