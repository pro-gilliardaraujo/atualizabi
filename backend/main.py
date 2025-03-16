from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid
import asyncio
import aiofiles
import json
from typing import Dict, Optional

load_dotenv()

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar Supabase
supabase: Client = create_client(
    os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# Diretório para arquivos base locais
LOCAL_BASE_DIR = Path("local_base_files")
LOCAL_BASE_DIR.mkdir(exist_ok=True)

# Arquivo de controle de versão local
VERSION_FILE = LOCAL_BASE_DIR / "versions.json"

# Configurações do Storage
STORAGE_BUCKET = "arquivos-bi"
STORAGE_BASE_FOLDER = "basefiles"  # Pasta para arquivos base/referência
STORAGE_UPLOAD_FOLDER = "uploaded"  # Pasta para arquivos enviados

class LocalVersionControl:
    def __init__(self):
        self.versions: Dict[str, str] = {}
        self.load_versions()

    def load_versions(self):
        """Carrega as versões dos arquivos base do arquivo de controle"""
        if VERSION_FILE.exists():
            try:
                with open(VERSION_FILE, 'r') as f:
                    self.versions = json.load(f)
            except:
                self.versions = {}

    def save_versions(self):
        """Salva as versões atuais no arquivo de controle"""
        with open(VERSION_FILE, 'w') as f:
            json.dump(self.versions, f)

    def get_version(self, report_type: str) -> Optional[str]:
        """Obtém a versão atual do arquivo base local"""
        return self.versions.get(report_type)

    def update_version(self, report_type: str, file_id: str):
        """Atualiza a versão de um arquivo base"""
        self.versions[report_type] = file_id
        self.save_versions()

version_control = LocalVersionControl()

def get_excel_last_modified_date(file_path):
    """Extrai a data de última modificação do arquivo Excel."""
    try:
        df = pd.read_excel(file_path)
        # Usar timestamp do arquivo e converter para UTC
        timestamp = datetime.fromtimestamp(os.path.getmtime(file_path))
        return timestamp.astimezone()  # Converte para timezone aware
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return None

async def upload_to_supabase(file_path: Path, bucket: str, storage_path: str):
    """Upload do arquivo para o Supabase Storage."""
    print(f"\n=== UPLOAD TO SUPABASE ===")
    print(f"Tentando fazer upload para: {bucket}/{storage_path}")
    with open(file_path, "rb") as f:
        try:
            response = supabase.storage.from_(bucket).upload(
                storage_path,
                f,
                {"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
            )
            print(f"Upload bem sucedido: {response}")
            return response
        except Exception as e:
            print(f"Erro no upload para Supabase: {e}")
            print(f"Detalhes do erro: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro no upload do arquivo: {str(e)}")

async def download_from_supabase(storage_path: str, local_path: Path):
    """Download do arquivo do Supabase Storage."""
    try:
        print("\n=== BAIXANDO ARQUIVO DO SUPABASE ===")
        print(f"Origem: {storage_path}")
        
        # Baixar o conteúdo do arquivo
        response = supabase.storage.from_(STORAGE_BUCKET).download(storage_path)
        
        # Garantir que o arquivo base local sempre tenha o mesmo nome
        final_path = LOCAL_BASE_DIR / f"base_{local_path.stem.split('_')[0]}.xlsx"
        print(f"Salvando em: {final_path}")
        
        # Remover arquivo existente se houver
        if final_path.exists():
            print("Removendo arquivo local existente...")
            os.remove(final_path)
            print("Arquivo antigo removido com sucesso")
        
        # Salvar novo arquivo
        print("Salvando novo arquivo...")
        with open(final_path, 'wb') as f:
            f.write(response)
        
        # Verificar se o arquivo foi salvo
        if final_path.exists():
            print("Novo arquivo salvo com sucesso")
            # Ler e mostrar conteúdo do novo arquivo
            df = pd.read_excel(final_path)
            print("\nConteúdo do novo arquivo:")
            print(df)
        else:
            print("ERRO: Arquivo não foi salvo corretamente")
            return False
        
        print("\n🔔 ATENÇÃO: ARQUIVO BASE ATUALIZADO!")
        print("→ Você já pode atualizar seu relatório no Power BI")
        print(f"→ Caminho do arquivo: {final_path}")
        print("→ As alterações já estão disponíveis\n")
        return True
    except Exception as e:
        print(f"Erro no download do Supabase: {e}")
        print(f"Detalhes do erro: {str(e)}")
        return False

async def get_base_file_info(report_type: str):
    """Obtém informações do arquivo base atual."""
    try:
        response = supabase.table("file_management").select("*").eq(
            "report_type", report_type
        ).eq("is_base_file", True).execute()
        
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar arquivo base: {e}")
        return None

async def sync_base_files():
    """Sincroniza todos os arquivos base do Supabase com o armazenamento local."""
    try:
        # Buscar todos os arquivos base
        response = supabase.table("file_management").select("*").eq("is_base_file", True).execute()
        
        for file_info in response.data:
            report_type = file_info["report_type"]
            file_id = file_info["id"]
            storage_path = file_info["storage_path"]
            
            # Verificar se precisamos atualizar este arquivo
            current_version = version_control.get_version(report_type)
            if current_version != str(file_id):
                # Baixar arquivo atualizado
                local_path = LOCAL_BASE_DIR / f"{report_type}.xlsx"
                if await download_from_supabase(storage_path, local_path):
                    version_control.update_version(report_type, str(file_id))
                    print(f"Arquivo base atualizado: {report_type}")
                else:
                    print(f"Erro ao atualizar arquivo base: {report_type}")

    except Exception as e:
        print(f"Erro na sincronização: {e}")

async def periodic_sync(interval_seconds: int = 300):
    """Executa a sincronização periodicamente."""
    while True:
        await sync_base_files()
        await asyncio.sleep(interval_seconds)

async def ensure_storage_folders():
    """Garante que as pastas necessárias existam no Storage."""
    print("\n=== VERIFICANDO ESTRUTURA DO STORAGE ===")
    try:
        # Lista de pastas necessárias para cada tipo de relatório
        report_types = ['vendas', 'estoque', 'financeiro', 'clientes']
        
        # Criar estrutura base
        for report_type in report_types:
            # Pasta base
            base_path = f"{STORAGE_BASE_FOLDER}/{report_type}/.keep"
            try:
                print(f"Verificando pasta base: {base_path}")
                supabase.storage.from_(STORAGE_BUCKET).upload(
                    base_path,
                    b"",  # arquivo vazio
                    {"content-type": "text/plain"}
                )
                print(f"Pasta base criada: {base_path}")
            except Exception as e:
                if "Duplicate" not in str(e):
                    print(f"Erro ao criar pasta base: {e}")
            
            # Pasta uploaded
            upload_path = f"{STORAGE_UPLOAD_FOLDER}/{report_type}/.keep"
            try:
                print(f"Verificando pasta upload: {upload_path}")
                supabase.storage.from_(STORAGE_BUCKET).upload(
                    upload_path,
                    b"",  # arquivo vazio
                    {"content-type": "text/plain"}
                )
                print(f"Pasta upload criada: {upload_path}")
            except Exception as e:
                if "Duplicate" not in str(e):
                    print(f"Erro ao criar pasta upload: {e}")
        
        print("Estrutura de pastas verificada/criada com sucesso")
    except Exception as e:
        print(f"Erro ao verificar/criar estrutura de pastas: {e}")

@app.on_event("startup")
async def startup_event():
    """Inicia a sincronização periódica quando o servidor iniciar."""
    # Garantir que as pastas existam
    await ensure_storage_folders()
    # Iniciar sincronização periódica
    asyncio.create_task(periodic_sync())

@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    reportType: str = Form(...)
):
    print(f"\n=== NOVO UPLOAD INICIADO ===")
    print(f"Tipo de relatório: {reportType}")
    print(f"Nome do arquivo: {file.filename}")

    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Apenas arquivos Excel são permitidos")

    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    file_id = str(uuid.uuid4())
    temp_file_path = temp_dir / f"temp_{file_id}_{file.filename}"
    print(f"Arquivo temporário: {temp_file_path}")
    
    try:
        # Salvar arquivo temporário
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        print("Arquivo temporário salvo com sucesso")

        last_modified = get_excel_last_modified_date(temp_file_path)
        if not last_modified:
            raise HTTPException(status_code=400, detail="Erro ao ler data do arquivo")
        print(f"Data de modificação do arquivo: {last_modified}")

        # Verificar se já existe um arquivo base
        base_file = await get_base_file_info(reportType)
        print(f"Arquivo base existente: {base_file}")
        
        # Preparar nome do arquivo base
        base_filename = f"base_{reportType}.xlsx"
        base_storage_path = f"{STORAGE_BASE_FOLDER}/{reportType}/{base_filename}"
        print(f"Caminho do arquivo base: {base_storage_path}")
        
        # Salvar arquivo na pasta de uploads (histórico)
        upload_storage_path = f"{STORAGE_UPLOAD_FOLDER}/{reportType}/{file_id}_{file.filename}"
        print(f"Salvando em uploaded/: {upload_storage_path}")
        await upload_to_supabase(temp_file_path, STORAGE_BUCKET, upload_storage_path)
        print("Upload para histórico concluído")

        file_data = {
            "report_type": reportType,
            "original_filename": file.filename,
            "storage_path": upload_storage_path,
            "status": "completed",
            "last_modified_date": last_modified.isoformat(),
            "is_base_file": False
        }

        if not base_file:
            print("\n=== CRIANDO PRIMEIRO ARQUIVO BASE ===")
            # Se não existe arquivo base, este será o primeiro
            print(f"Tentando criar arquivo base em: {base_storage_path}")
            await upload_to_supabase(temp_file_path, STORAGE_BUCKET, base_storage_path)
            print("Upload do arquivo base concluído")
            
            # Atualizar dados para arquivo base
            file_data["is_base_file"] = True
            file_data["storage_path"] = base_storage_path
            
            # Inserir registro na tabela
            print("Inserindo registro na tabela file_management")
            response = supabase.table("file_management").insert(file_data).execute()
            print(f"Registro inserido: {response.data}")
            
            # Atualizar arquivo base local
            local_path = LOCAL_BASE_DIR / base_filename
            print(f"Baixando arquivo base para: {local_path}")
            await download_from_supabase(base_storage_path, local_path)
            version_control.update_version(reportType, file_id)
            print("Arquivo base local atualizado")
            
            return {"message": "Arquivo base criado com sucesso"}

        # Se já existe um arquivo base, verificar a data
        print("\n=== VERIFICANDO ATUALIZAÇÃO DO ARQUIVO BASE ===")
        base_date = datetime.fromisoformat(base_file["last_modified_date"])
        print(f"Data do arquivo base: {base_date}")
        print(f"Data do novo arquivo: {last_modified}")
        
        if last_modified > base_date:
            print("Novo arquivo é mais recente, atualizando base")
            # Deletar arquivo base antigo antes de fazer upload do novo
            await delete_from_supabase(STORAGE_BUCKET, base_storage_path)
            # Arquivo é mais novo, atualizar base
            await upload_to_supabase(temp_file_path, STORAGE_BUCKET, base_storage_path)
            print("Upload do novo arquivo base concluído")
            
            # Atualizar registro do arquivo base antigo
            print("Atualizando registro antigo")
            supabase.table("file_management").update(
                {"is_base_file": False}
            ).eq("id", base_file["id"]).execute()
            
            # Criar novo registro para o arquivo base
            file_data["is_base_file"] = True
            file_data["storage_path"] = base_storage_path
            print("Inserindo novo registro base")
            response = supabase.table("file_management").insert(file_data).execute()
            print(f"Novo registro inserido: {response.data}")
            
            # Atualizar arquivo base local
            local_path = LOCAL_BASE_DIR / base_filename
            print(f"Baixando novo arquivo base para: {local_path}")
            await download_from_supabase(base_storage_path, local_path)
            version_control.update_version(reportType, file_id)
            print("Arquivo base local atualizado")
            
            return {"message": "Arquivo base atualizado com sucesso"}
        else:
            print("Arquivo atual é mais antigo, mantendo base existente")
            # Apenas registrar o arquivo enviado
            response = supabase.table("file_management").insert(file_data).execute()
            print(f"Registro de histórico inserido: {response.data}")
            return {"message": "Arquivo registrado, mas base mantida pois é mais recente"}

    except Exception as e:
        print(f"\n=== ERRO NO PROCESSO DE UPLOAD ===")
        print(f"Erro detalhado: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path.exists():
            os.remove(temp_file_path)
            print("Arquivo temporário removido")

@app.get("/sync")
async def force_sync():
    """Endpoint para forçar uma sincronização manual."""
    await sync_base_files()
    return {"message": "Sincronização concluída"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

async def delete_from_supabase(bucket: str, storage_path: str):
    """Deleta um arquivo do Supabase Storage."""
    try:
        print(f"\n=== DELETANDO ARQUIVO DO SUPABASE ===")
        print(f"Deletando: {bucket}/{storage_path}")
        supabase.storage.from_(bucket).remove([storage_path])
        print("Arquivo deletado com sucesso")
        return True
    except Exception as e:
        print(f"Erro ao deletar arquivo: {e}")
        return False 