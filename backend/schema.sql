-- Criar enum para status do arquivo
CREATE TYPE file_status AS ENUM ('pending', 'processing', 'completed', 'error');

-- Criar tabela para gerenciar arquivos
CREATE TABLE file_management (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,
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
CREATE INDEX idx_file_management_report_type ON file_management(report_type);
CREATE INDEX idx_file_management_status ON file_management(status);
CREATE INDEX idx_file_management_is_base_file ON file_management(is_base_file);

-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para atualizar updated_at
CREATE TRIGGER update_file_management_updated_at
    BEFORE UPDATE ON file_management
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 