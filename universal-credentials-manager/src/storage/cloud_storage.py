"""
☁️ Cloud Storage Universal
Suporte para AWS S3, Azure Blob e Google Cloud Storage
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

logger = logging.getLogger("cloud-storage")

class CloudStorageInterface(ABC):
    """Interface para diferentes provedores de cloud storage"""
    
    @abstractmethod
    async def upload_file(self, key: str, content: str, metadata: Dict[str, str] = None) -> bool:
        """Upload de arquivo"""
        pass
    
    @abstractmethod
    async def download_file(self, key: str) -> Optional[str]:
        """Download de arquivo"""
        pass
    
    @abstractmethod
    async def delete_file(self, key: str) -> bool:
        """Deletar arquivo"""
        pass
    
    @abstractmethod
    async def list_files(self, prefix: str = "") -> List[str]:
        """Listar arquivos"""
        pass
    
    @abstractmethod
    async def file_exists(self, key: str) -> bool:
        """Verificar se arquivo existe"""
        pass

class AWSS3Storage(CloudStorageInterface):
    """Implementação para AWS S3"""
    
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.region = region
        self.s3_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa cliente S3"""
        try:
            import boto3
            from botocore.config import Config
            
            # Configuração com retry e timeout
            config = Config(
                region_name=self.region,
                retries={'max_attempts': 3, 'mode': 'adaptive'},
                max_pool_connections=50
            )
            
            # Credenciais via variáveis de ambiente ou IAM role
            self.s3_client = boto3.client('s3', config=config)
            
            logger.info(f"✅ Cliente S3 inicializado - Bucket: {self.bucket_name}")
            
        except ImportError:
            logger.error("❌ boto3 não instalado. Execute: pip install boto3")
            raise
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar S3: {e}")
            raise
    
    async def upload_file(self, key: str, content: str, metadata: Dict[str, str] = None) -> bool:
        """Upload arquivo para S3"""
        try:
            # Preparar metadados
            s3_metadata = {
                'uploaded_at': datetime.now().isoformat(),
                'content_type': 'application/json',
                'encryption': 'AES256'
            }
            
            if metadata:
                s3_metadata.update(metadata)
            
            # Upload com criptografia server-side
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=content.encode('utf-8'),
                    Metadata=s3_metadata,
                    ServerSideEncryption='AES256',
                    ContentType='application/json'
                )
            )
            
            logger.info(f"✅ Arquivo enviado para S3: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no upload S3 {key}: {e}")
            return False
    
    async def download_file(self, key: str) -> Optional[str]:
        """Download arquivo do S3"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
            )
            
            content = response['Body'].read().decode('utf-8')
            logger.info(f"✅ Arquivo baixado do S3: {key}")
            return content
            
        except self.s3_client.exceptions.NoSuchKey:
            logger.warning(f"📁 Arquivo não encontrado no S3: {key}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro no download S3 {key}: {e}")
            return None
    
    async def delete_file(self, key: str) -> bool:
        """Deletar arquivo do S3"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
            )
            
            logger.info(f"🗑️ Arquivo removido do S3: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao deletar S3 {key}: {e}")
            return False
    
    async def list_files(self, prefix: str = "") -> List[str]:
        """Listar arquivos do S3"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix
                )
            )
            
            files = []
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
            
            logger.info(f"📋 {len(files)} arquivos encontrados no S3 (prefix: {prefix})")
            return files
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar S3: {e}")
            return []
    
    async def file_exists(self, key: str) -> bool:
        """Verificar se arquivo existe no S3"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
            )
            return True
            
        except self.s3_client.exceptions.NoSuchKey:
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao verificar S3 {key}: {e}")
            return False
    
    async def create_backup(self, key: str) -> bool:
        """Criar backup com timestamp"""
        try:
            # Gerar chave de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_key = f"backups/{key}.{timestamp}"
            
            # Copiar arquivo
            copy_source = {'Bucket': self.bucket_name, 'Key': key}
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.copy_object(
                    CopySource=copy_source,
                    Bucket=self.bucket_name,
                    Key=backup_key,
                    ServerSideEncryption='AES256'
                )
            )
            
            logger.info(f"💾 Backup criado: {backup_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            return False

class LocalFileStorage(CloudStorageInterface):
    """Implementação para armazenamento local (fallback)"""
    
    def __init__(self, base_path: str = "config/projects"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        logger.info(f"📁 Storage local inicializado: {base_path}")
    
    async def upload_file(self, key: str, content: str, metadata: Dict[str, str] = None) -> bool:
        """Salvar arquivo localmente"""
        try:
            file_path = os.path.join(self.base_path, key)
            
            # Criar diretórios se necessário
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Salvar arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"💾 Arquivo salvo localmente: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar local {key}: {e}")
            return False
    
    async def download_file(self, key: str) -> Optional[str]:
        """Ler arquivo local"""
        try:
            file_path = os.path.join(self.base_path, key)
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"📖 Arquivo lido localmente: {file_path}")
            return content
            
        except Exception as e:
            logger.error(f"❌ Erro ao ler local {key}: {e}")
            return None
    
    async def delete_file(self, key: str) -> bool:
        """Deletar arquivo local"""
        try:
            file_path = os.path.join(self.base_path, key)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🗑️ Arquivo removido localmente: {file_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao deletar local {key}: {e}")
            return False
    
    async def list_files(self, prefix: str = "") -> List[str]:
        """Listar arquivos locais"""
        try:
            files = []
            search_path = os.path.join(self.base_path, prefix)
            
            if os.path.isdir(search_path):
                for root, dirs, filenames in os.walk(search_path):
                    for filename in filenames:
                        full_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(full_path, self.base_path)
                        files.append(relative_path.replace('\\', '/'))  # Normalizar separadores
            
            logger.info(f"📋 {len(files)} arquivos encontrados localmente")
            return files
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar local: {e}")
            return []
    
    async def file_exists(self, key: str) -> bool:
        """Verificar se arquivo existe localmente"""
        file_path = os.path.join(self.base_path, key)
        return os.path.exists(file_path)

class HybridStorage:
    """Storage híbrido: Local + Cloud com sincronização"""
    
    def __init__(self, 
                 cloud_provider: str = "s3",
                 bucket_name: str = None,
                 local_fallback: bool = True):
        
        self.local_storage = LocalFileStorage()
        self.cloud_storage = None
        self.cloud_enabled = False
        
        # Configurar cloud storage
        if cloud_provider == "s3" and bucket_name:
            try:
                aws_region = os.getenv("AWS_REGION", "us-east-1")
                self.cloud_storage = AWSS3Storage(bucket_name, aws_region)
                self.cloud_enabled = True
                logger.info(f"☁️ Storage híbrido: Local + S3 ({bucket_name})")
            except Exception as e:
                logger.warning(f"⚠️ Falha ao configurar S3, usando apenas local: {e}")
        
        if not self.cloud_enabled and local_fallback:
            logger.info("📁 Storage local ativo (cloud não configurado)")
    
    async def save_project_data(self, project_name: str, data: Dict[str, Any]) -> bool:
        """Salvar dados do projeto (local + cloud)"""
        key = f"projects/{project_name}.json"
        content = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Salvar localmente sempre
        local_success = await self.local_storage.upload_file(key, content)
        
        # Salvar na nuvem se disponível
        cloud_success = True
        if self.cloud_enabled:
            # Criar backup antes de atualizar
            if await self.cloud_storage.file_exists(key):
                await self.cloud_storage.create_backup(key)
            
            cloud_success = await self.cloud_storage.upload_file(key, content, {
                'project': project_name,
                'version': '1.0'
            })
        
        return local_success and cloud_success
    
    async def load_project_data(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Carregar dados do projeto (cloud primeiro, local como fallback)"""
        key = f"projects/{project_name}.json"
        
        # Tentar cloud primeiro
        if self.cloud_enabled:
            content = await self.cloud_storage.download_file(key)
            if content:
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON inválido do cloud: {e}")
        
        # Fallback para local
        content = await self.local_storage.download_file(key)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON inválido local: {e}")
        
        return None
    
    async def list_projects(self) -> List[str]:
        """Listar projetos disponíveis"""
        projects = set()
        
        # Listar do cloud
        if self.cloud_enabled:
            cloud_files = await self.cloud_storage.list_files("projects/")
            for file_key in cloud_files:
                if file_key.endswith('.json'):
                    project_name = os.path.basename(file_key).replace('.json', '')
                    projects.add(project_name)
        
        # Listar local
        local_files = await self.local_storage.list_files("projects/")
        for file_key in local_files:
            if file_key.endswith('.json'):
                project_name = os.path.basename(file_key).replace('.json', '')
                projects.add(project_name)
        
        return sorted(list(projects))
    
    async def sync_to_cloud(self, project_name: str = None) -> bool:
        """Sincronizar local para cloud"""
        if not self.cloud_enabled:
            logger.warning("⚠️ Cloud storage não configurado")
            return False
        
        try:
            if project_name:
                # Sincronizar projeto específico
                key = f"projects/{project_name}.json"
                content = await self.local_storage.download_file(key)
                if content:
                    return await self.cloud_storage.upload_file(key, content)
            else:
                # Sincronizar todos os projetos
                local_files = await self.local_storage.list_files("projects/")
                for file_key in local_files:
                    if file_key.endswith('.json'):
                        content = await self.local_storage.download_file(file_key)
                        if content:
                            await self.cloud_storage.upload_file(file_key, content)
                
                logger.info(f"🔄 {len(local_files)} projetos sincronizados para cloud")
                return True
            
        except Exception as e:
            logger.error(f"❌ Erro na sincronização: {e}")
            return False
        
        return False

# Factory para criar storage baseado na configuração
def create_storage(storage_type: str = "hybrid", **kwargs) -> HybridStorage:
    """Factory para criar instância de storage"""
    
    if storage_type == "local":
        return HybridStorage(cloud_provider=None, local_fallback=True)
    elif storage_type == "s3":
        bucket_name = kwargs.get("bucket_name") or os.getenv("AWS_S3_BUCKET")
        if not bucket_name:
            raise ValueError("bucket_name é obrigatório para S3 storage")
        return HybridStorage(cloud_provider="s3", bucket_name=bucket_name)
    elif storage_type == "hybrid":
        bucket_name = kwargs.get("bucket_name") or os.getenv("AWS_S3_BUCKET")
        return HybridStorage(cloud_provider="s3", bucket_name=bucket_name, local_fallback=True)
    else:
        raise ValueError(f"Tipo de storage não suportado: {storage_type}")

# Instância global
storage = create_storage(
    storage_type=os.getenv("STORAGE_TYPE", "hybrid"),
    bucket_name=os.getenv("AWS_S3_BUCKET")
)