"""
🔐 Cliente para Universal Credentials Manager
Cliente para obter credenciais do UCM em vez de credentials.json
"""

import os
import httpx
import asyncio
from typing import Dict, Any, Optional
from src.utils.logger import logger

class UCMCredentialsClient:
    """Cliente para Universal Credentials Manager"""
    
    def __init__(self, 
                 ucm_url: str = None,
                 project_name: str = "omie-mcp",
                 company_key: str = None):
        
        # Configuração do UCM
        self.ucm_url = ucm_url or os.getenv("UCM_API_URL", "http://localhost:8100")
        self.project_name = project_name
        self.company_key = company_key or os.getenv("UCM_COMPANY_KEY", "empresa_principal")
        
        # Auth token (se usando autenticação)
        self.auth_token = os.getenv("UCM_AUTH_TOKEN")
        
        # Cache de credenciais
        self._credentials_cache = None
        self._cache_expires_at = None
        
        logger.info(f"🔐 UCM Client inicializado: {self.ucm_url}/{self.project_name}/{self.company_key}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Headers para requisições UCM"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Omie-MCP/1.0"
        }
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        return headers
    
    async def _make_ucm_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Fazer requisição para UCM"""
        url = f"{self.ucm_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(url, json=data, headers=headers)
                else:
                    raise ValueError(f"Método não suportado: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.ConnectError:
            logger.error(f"❌ Não foi possível conectar ao UCM em {self.ucm_url}")
            logger.error("💡 Certifique-se que o UCM está rodando: python src/api/server.py")
            raise Exception("UCM não disponível - verifique se está rodando")
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Erro HTTP {e.response.status_code} do UCM: {e.response.text}")
            raise Exception(f"Erro UCM HTTP {e.response.status_code}")
        except Exception as e:
            logger.error(f"❌ Erro na comunicação com UCM: {e}")
            raise Exception(f"Erro UCM: {e}")
    
    async def get_credentials(self, force_refresh: bool = False) -> Dict[str, str]:
        """Obter credenciais do UCM"""
        
        # Verificar cache se não forçar refresh
        if not force_refresh and self._credentials_cache:
            import time
            if self._cache_expires_at and time.time() < self._cache_expires_at:
                logger.debug("🔄 Usando credenciais do cache")
                return self._credentials_cache
        
        try:
            logger.info(f"🔐 Obtendo credenciais UCM: {self.project_name}/{self.company_key}")
            
            endpoint = f"/api/v1/projects/{self.project_name}/credentials/{self.company_key}"
            result = await self._make_ucm_request(endpoint)
            
            # Extrair credenciais
            credentials = {
                "app_key": result.get("app_key", ""),
                "app_secret": result.get("app_secret", ""),
                "base_url": result.get("base_url", "https://app.omie.com.br/api/v1")
            }
            
            # Validar credenciais
            if not credentials["app_key"] or not credentials["app_secret"]:
                raise Exception("Credenciais incompletas recebidas do UCM")
            
            # Atualizar cache
            self._credentials_cache = credentials
            import time
            self._cache_expires_at = time.time() + 300  # Cache por 5 minutos
            
            logger.info(f"✅ Credenciais UCM obtidas com sucesso")
            return credentials
            
        except Exception as e:
            logger.error(f"❌ Falha ao obter credenciais do UCM: {e}")
            
            # Fallback para credentials.json local se UCM falhar
            return await self._fallback_credentials()
    
    async def _fallback_credentials(self) -> Dict[str, str]:
        """Fallback para credentials.json se UCM não estiver disponível"""
        logger.warning("⚠️ Usando fallback: credentials.json local")
        
        try:
            import json
            from pathlib import Path
            
            project_root = Path(__file__).parent.parent.parent
            credentials_path = project_root / "credentials.json"
            
            if not credentials_path.exists():
                raise FileNotFoundError("Arquivo credentials.json não encontrado")
            
            with open(credentials_path, 'r') as f:
                creds = json.load(f)
            
            fallback_creds = {
                "app_key": creds.get("app_key", ""),
                "app_secret": creds.get("app_secret", ""),
                "base_url": creds.get("base_url", "https://app.omie.com.br/api/v1")
            }
            
            if not fallback_creds["app_key"] or not fallback_creds["app_secret"]:
                raise ValueError("Credenciais inválidas no arquivo local")
            
            logger.info("✅ Credenciais locais carregadas com sucesso (fallback)")
            return fallback_creds
            
        except Exception as e:
            logger.error(f"❌ Falha no fallback de credenciais: {e}")
            raise Exception("Não foi possível obter credenciais de nenhuma fonte")
    
    async def test_connection(self) -> bool:
        """Testar conexão com UCM"""
        try:
            result = await self._make_ucm_request("/")
            logger.info(f"✅ UCM conectado: {result.get('service', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"❌ UCM não conectado: {e}")
            return False
    
    async def list_companies(self) -> list:
        """Listar empresas disponíveis no projeto"""
        try:
            endpoint = f"/api/v1/projects/{self.project_name}/companies"
            result = await self._make_ucm_request(endpoint)
            
            companies = []
            for company in result:
                companies.append({
                    "key": company["key"],
                    "name": company["name"],
                    "active": company["active"],
                    "has_credentials": company["has_credentials"]
                })
            
            logger.info(f"📋 {len(companies)} empresas encontradas no UCM")
            return companies
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar empresas: {e}")
            return []
    
    async def refresh_credentials(self) -> Dict[str, str]:
        """Forçar refresh das credenciais"""
        return await self.get_credentials(force_refresh=True)
    
    def set_company(self, company_key: str):
        """Trocar empresa ativa"""
        self.company_key = company_key
        self._credentials_cache = None  # Invalidar cache
        logger.info(f"🏢 Empresa alterada para: {company_key}")

# Instância global
ucm_client = UCMCredentialsClient()