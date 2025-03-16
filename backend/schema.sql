-- Criar enum para status do arquivo
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'file_status') THEN
        CREATE TYPE file_status AS ENUM ('pending', 'processing', 'completed', 'error');
    END IF;
END $$;

-- Remover tabela existente e seu trigger
DROP TRIGGER IF EXISTS update_file_management_updated_at ON file_management;
DROP TABLE IF EXISTS file_management;

-- Criar tabela para gerenciar arquivos
CREATE TABLE file_management (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    page VARCHAR(50) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    storage_path VARCHAR(255) NOT NULL,
    status file_status DEFAULT 'pending',
    is_base_file BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified_date TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Criar índices
CREATE INDEX idx_file_management_category ON file_management(category);
CREATE INDEX idx_file_management_page ON file_management(page);
CREATE INDEX idx_file_management_status ON file_management(status);
CREATE INDEX idx_file_management_is_base_file ON file_management(is_base_file);

-- Criar trigger para atualizar updated_at (usando a função existente)
CREATE TRIGGER update_file_management_updated_at
    BEFORE UPDATE ON file_management
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 