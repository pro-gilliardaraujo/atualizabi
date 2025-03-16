import pandas as pd
from datetime import datetime
import numpy as np

def create_updated_file(tipo_relatorio):
    """Cria um arquivo de teste atualizado com campos tratados."""
    # Data e hora atual formatada
    data_atual = datetime.now().strftime('%Y-%m-%d')
    hora_atual = datetime.now().strftime('%H:%M:%S')
    
    # Número de linhas para criar
    num_linhas = 10
    
    # Criar múltiplas linhas de dados de teste
    data = {
        'data_atualizacao': [data_atual] * num_linhas,
        'hora_atualizacao': [hora_atual] * num_linhas,
        'nome_teste': [
            f'TESTE LINHA {i+1} - {tipo_relatorio.upper()}'
            for i in range(num_linhas)
        ],
        'valor_teste': [
            round(float(np.random.randint(1000, 5000)), 2)
            for _ in range(num_linhas)
        ],
        'status': [
            np.random.choice(['NOVO', 'ATUALIZADO', 'EM ANÁLISE', 'REVISADO'])
            for _ in range(num_linhas)
        ],
        'observacao': [
            f'Observação detalhada do registro {i+1} - Teste de múltiplas linhas'
            for i in range(num_linhas)
        ]
    }

    # Criar DataFrame
    df = pd.DataFrame(data)
    
    # Garantir tipos de dados corretos
    df['data_atualizacao'] = pd.to_datetime(df['data_atualizacao']).dt.date
    df['hora_atualizacao'] = pd.to_datetime(df['hora_atualizacao'], format='%H:%M:%S').dt.time
    df['valor_teste'] = df['valor_teste'].astype(float)
    
    # Ordenar por valor_teste para melhor visualização
    df = df.sort_values('valor_teste', ascending=False)
    
    # Nome do arquivo
    filename = f'novo_{tipo_relatorio.lower()}.xlsx'
    
    # Salvar arquivo com formatação específica
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    print(f"\n=== ARQUIVO ATUALIZADO CRIADO ===")
    print(f"Nome do arquivo: {filename}")
    print(f"Data de atualização: {data_atual}")
    print(f"Hora de atualização: {hora_atual}")
    print(f"Número de linhas: {len(df)}")
    print("\nConteúdo do arquivo:")
    print(df)
    print("\nResumo dos valores:")
    print(f"Média dos valores: {df['valor_teste'].mean():.2f}")
    print(f"Valor máximo: {df['valor_teste'].max():.2f}")
    print(f"Valor mínimo: {df['valor_teste'].min():.2f}")
    print("\nColunas:")
    for col in df.columns:
        print(f"- {col}: {df[col].dtype}")

if __name__ == "__main__":
    # Criar arquivo atualizado de vendas
    create_updated_file("vendas") 