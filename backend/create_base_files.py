import pandas as pd
from datetime import datetime, timedelta

def create_base_files():
    # Criar dados para o primeiro arquivo
    data1 = {
        'data_atualizacao': [datetime.now().strftime('%Y-%m-%d')],
        'hora_atualizacao': [datetime.now().strftime('%H:%M:%S')],
        'nome_teste': ['Arquivo Base 1']
    }

    # Criar dados para o segundo arquivo (com data anterior)
    data2 = {
        'data_atualizacao': [(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')],
        'hora_atualizacao': [(datetime.now() - timedelta(days=1)).strftime('%H:%M:%S')],
        'nome_teste': ['Arquivo Base 2']
    }

    # Criar DataFrames
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)

    # Salvar arquivos
    df1.to_excel('base_vendas.xlsx', index=False)
    df2.to_excel('base_estoque.xlsx', index=False)

    print("Arquivos base criados com sucesso!")

if __name__ == "__main__":
    create_base_files() 