# Sistema de Atualização de Relatórios Power BI

## Estrutura Atual

### Componentes
- **Frontend**: Next.js (porta 3000)
- **Backend**: FastAPI (porta 8000)
- **Storage**: Supabase
- **Banco de Dados**: Supabase (PostgreSQL)

### Fluxo de Funcionamento
1. **Armazenamento de Arquivos**
   - `basefiles/`: Contém os arquivos base atuais (referência para Power BI)
   - `uploaded/`: Histórico de todos os arquivos enviados
   - `local_base_files/`: Pasta local com arquivos base sincronizados

2. **Processo de Atualização**
   - Upload do arquivo via frontend
   - Verificação de data/hora de atualização
   - Se mais recente: atualiza arquivo base no Supabase e localmente
   - Mantém histórico de todos os uploads
   - Sincronização automática a cada 5 minutos

## Como Testar

1. **Iniciar os Servidores**
   ```bash
   # Backend
   cd backend
   uvicorn main:app --reload

   # Frontend
   cd frontend
   npm run dev
   ```

2. **Criar Arquivo de Teste**
   ```bash
   cd backend
   python create_updated_file.py
   ```

3. **Testar Upload**
   - Acesse `http://localhost:3000`
   - Selecione tipo de relatório
   - Faça upload do arquivo
   - Verifique logs no terminal do backend
   - Confirme atualização no Power BI

## Adicionando Novas Categorias

1. **Modificar Lista de Relatórios**
   - Em `frontend/app/page.tsx`, atualizar array `reportTypes`:
   ```typescript
   const reportTypes = [
     { id: 'vendas', name: 'Relatório de Vendas' },
     { id: 'estoque', name: 'Relatório de Estoque' },
     // Adicionar novas categorias aqui
   ];
   ```

2. **Atualizar Backend**
   - Em `backend/main.py`, atualizar lista em `ensure_storage_folders()`:
   ```python
   report_types = ['vendas', 'estoque', 'financeiro', 'clientes']
   # Adicionar novas categorias aqui
   ```

3. **Criar Estrutura no Supabase**
   - O sistema criará automaticamente as pastas necessárias
   - Estrutura: `basefiles/nova_categoria/` e `uploaded/nova_categoria/`

## Adaptação para Estrutura Categoria/Página

Para adaptar o sistema para uma estrutura de categoria/página:

1. **Modificar Modelo de Dados**
   ```sql
   -- Adicionar à tabela file_management
   ALTER TABLE file_management ADD COLUMN category VARCHAR(50);
   ALTER TABLE file_management ADD COLUMN page VARCHAR(50);
   ```

2. **Atualizar Frontend**
   ```typescript
   // Estrutura sugerida
   const categories = [
     {
       id: 'categoria1',
       name: 'Categoria 1',
       pages: [
         { id: 'pagina1', name: 'Página 1' },
         { id: 'pagina2', name: 'Página 2' }
       ]
     }
   ];
   ```

3. **Modificar Estrutura de Pastas**
   - Nova estrutura:
   ```
   basefiles/
     categoria1/
       pagina1/
       pagina2/
   uploaded/
     categoria1/
       pagina1/
       pagina2/
   ```

4. **Ajustar Funções do Backend**
   - Modificar `upload_file()` para aceitar categoria e página
   - Atualizar caminhos de armazenamento
   - Ajustar sincronização para estrutura hierárquica

## Adaptando para Dados Reais

1. **Modificar Função de Validação**
   ```python
   def validate_excel_file(file_path):
       """Validar estrutura do arquivo conforme necessidade real"""
       df = pd.read_excel(file_path)
       required_columns = [
           # Adicionar colunas necessárias
       ]
       return all(col in df.columns for col in required_columns)
   ```

2. **Ajustar Extração de Data**
   ```python
   def get_excel_last_modified_date(file_path):
       """Extrair data de atualização da coluna correta"""
       df = pd.read_excel(file_path)
       # Ajustar para usar coluna específica de data
       return df['data_atualizacao'].max()
   ```

3. **Configurar Tratamento de Dados**
   - Modificar `create_updated_file.py` para estrutura real
   - Ajustar tipos de dados conforme necessidade
   - Implementar validações específicas

## Observações Importantes

1. **Segurança**
   - Chaves do Supabase em variáveis de ambiente
   - Validação de tipos de arquivo
   - Controle de acesso por usuário (a ser implementado)

2. **Manutenção**
   - Logs detalhados para debug
   - Backup automático de arquivos
   - Monitoramento de sincronização

3. **Performance**
   - Arquivos processados em diretório temporário
   - Limpeza automática de arquivos temporários
   - Otimização de consultas ao Supabase 