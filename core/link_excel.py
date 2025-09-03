import pandas as pd
import core.entidades as entity

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

