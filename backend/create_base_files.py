import pandas as pd
from pathlib import Path
from datetime import datetime

# Estrutura de categorias e páginas
report_types = [
    { 
        'id': 'plantio',
        'name': 'Plantio',
        'pages': [
            { 'id': 'frente1', 'name': 'Frente 1' }
        ]
    },
    {
        'id': 'colheita',
        'name': 'Colheita',
        'pages': [
            { 'id': 'arakaki', 'name': 'Arakaki' },
            { 'id': 'ituiutaba', 'name': 'Ituiutaba' },
            { 'id': 'iturama', 'name': 'Iturama' },
            { 'id': 'ouroeste', 'name': 'Ouroeste' },
            { 'id': 'zirleno', 'name': 'Zirleno' }
        ]
    },
    {
        'id': 'cav',
        'name': 'CAV',
        'pages': [
            { 'id': 'frente1', 'name': 'Frente 1' },
            { 'id': 'frente2', 'name': 'Frente 2' },
            { 'id': 'frente3', 'name': 'Frente 3' },
            { 'id': 'frente4', 'name': 'Frente 4' }
        ]
    },
    {
        'id': 'bonificacoes',
        'name': 'Bonificações',
        'pages': [
            { 'id': 'geral', 'name': 'Geral' },
            { 'id': 'individual', 'name': 'Individual' }
        ]
    }
]

def create_empty_base_file(category: str, page: str):
    """Cria um arquivo base vazio para uma categoria e página específicas."""
    # Criar diretório local_base_files se não existir
    base_dir = Path('local_base_files')
    base_dir.mkdir(exist_ok=True)
    
    # Nome do arquivo base
    filename = f"base_{category}_{page}.xlsx"
    filepath = base_dir / filename
    
    # Criar DataFrame vazio com colunas básicas
    now = datetime.now()
    df = pd.DataFrame({
        'data_atualizacao': [now.strftime('%Y-%m-%d')],
        'hora_atualizacao': [now.strftime('%H:%M:%S')],
        'nome_teste': ['Arquivo Base']
    })
    
    # Salvar arquivo
    df.to_excel(filepath, index=False)
    print(f"Arquivo base criado: {filepath}")

def main():
    """Cria todos os arquivos base vazios."""
    print("=== CRIANDO ARQUIVOS BASE VAZIOS ===")
    
    for category in report_types:
        for page in category['pages']:
            create_empty_base_file(category['id'], page['id'])
    
    print("\nTodos os arquivos base foram criados com sucesso!")

if __name__ == "__main__":
    main() 