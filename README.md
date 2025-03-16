# Sistema de Atualização de Relatórios

Este projeto consiste em um sistema para atualizar arquivos Excel que servem como base para relatórios do Power BI.

## Estrutura do Projeto

- `frontend/`: Aplicação Next.js com interface para upload de arquivos
- `backend/`: API FastAPI para processamento dos arquivos Excel

## Requisitos

- Node.js 18+ (Frontend)
- Python 3.8+ (Backend)
- npm ou yarn

## Como Executar

### Backend (Python/FastAPI)

1. Entre no diretório do backend:
```bash
cd backend
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o servidor:
```bash
uvicorn main:app --reload
```

O backend estará rodando em `http://localhost:8000`

### Frontend (Next.js)

1. Em outro terminal, entre no diretório do frontend:
```bash
cd frontend
```

2. Instale as dependências:
```bash
npm install
# ou
yarn install
```

3. Execute o servidor de desenvolvimento:
```bash
npm run dev
# ou
yarn dev
```

O frontend estará disponível em `http://localhost:3000`

## Como Usar

1. Acesse `http://localhost:3000` no seu navegador
2. Selecione o tipo de relatório que deseja atualizar
3. Escolha o arquivo Excel que contém os dados mais recentes
4. Clique em "Enviar Arquivo"

O sistema irá:
- Verificar se já existe um arquivo base para o tipo de relatório selecionado
- Se não existir, criar um novo arquivo base
- Se existir, comparar as datas de modificação e atualizar apenas se o arquivo enviado for mais recente

## Observações

- Os arquivos base são armazenados no diretório `backend/base_files/`
- Apenas arquivos Excel (.xlsx, .xls) são aceitos
- A comparação de datas é feita com base na data de modificação do arquivo 