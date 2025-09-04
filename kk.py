from core.link_excel import *
import core.entidades as entity

pontos = listar_pontos_turisticos_mais_avaliados()
print("Pontos turísticos mais bem avaliados:")
for ponto in pontos:
        print(f"ID: {ponto[0]} | Total de Avaliações: {ponto[1]} | Média: {ponto[2]}")
