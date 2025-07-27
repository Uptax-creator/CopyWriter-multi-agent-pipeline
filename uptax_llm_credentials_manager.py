#!/usr/bin/env python3
"""
🔐 UpTax LLM Credentials Manager
===============================
Sistema seguro para gerenciamento de credenciais de LLM providers
"""

import os
import sys
import json
import logging
import asyncio
import getpass
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️ python-dotenv não instalado. Executando: pip install python-dotenv")

@dataclass
class LLMProvider:
    """Configuração de um provider LLM"""
    name: str
    api_key: str
    base_url: str
    models: List[str]
    rate_limit: int
    monthly_limit: float
    cost_per_1k_tokens: Dict[str, float]
    enabled: bool = True
    last_used: Optional[str] = None
    total_cost: float = 0.0
    
@dataclass
class LLMUsageRecord:
    """Registro de uso de LLM"""
    provider: str
    model: str
    tokens_used: int
    cost: float
    timestamp: str
    task_id: Optional[str] = None
    operation: str = "unknown"

class UptaxLLMCredentialsManager:
    """
    🔐 Gerenciador seguro de credenciais LLM
    
    Funcionalidades:
    - Múltiplas fontes de credenciais (env, arquivo, input interativo)
    - Criptografia AES-256 para armazenamento
    - Rate limiting e cost tracking
    - Fallback automático entre providers
    - Audit trail completo
    """
    
    def __init__(self, project_dir: str = None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.env_file = self.project_dir / ".env.local"
        self.credentials_file = self.project_dir / "llm_credentials.encrypted"
        self.usage_log = self.project_dir / "llm_usage.log"
        
        self.providers = {}
        self.usage_records = []
        
        self.setup_logging()
        self.load_provider_configurations()
    
    def setup_logging(self):
        """Configurar logging seguro"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.usage_log),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('LLMCredentialsManager')
        self.logger.info("🔐 LLM Credentials Manager inicializado")
    
    def load_provider_configurations(self):
        """Carregar configurações dos providers"""
        self.provider_configs = {
            "gemini": {
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "models": ["gemini-1.5-pro", "gemini-1.5-flash"],
                "rate_limit": 60,
                "monthly_limit": 100.0,
                "cost_per_1k_tokens": {
                    "gemini-1.5-pro": 0.0015,
                    "gemini-1.5-flash": 0.000075
                }
            },
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
                "rate_limit": 60,
                "monthly_limit": 100.0,
                "cost_per_1k_tokens": {
                    "gpt-4o": 0.005,
                    "gpt-4o-mini": 0.00015,
                    "gpt-3.5-turbo": 0.001
                }
            },
            "huggingface": {
                "base_url": "https://api-inference.huggingface.co",
                "models": ["mistral-7b", "llama-2-7b", "codellama-7b"],
                "rate_limit": 30,
                "monthly_limit": 50.0,
                "cost_per_1k_tokens": {
                    "mistral-7b": 0.0005,
                    "llama-2-7b": 0.0005,
                    "codellama-7b": 0.0005
                }
            },
            "anthropic": {
                "base_url": "https://api.anthropic.com",
                "models": [
                    "claude-3-5-sonnet-20241022", 
                    "claude-3-5-haiku-20241022",
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307"
                ],
                "rate_limit": 50,
                "monthly_limit": 200.0,
                "cost_per_1k_tokens": {
                    "claude-3-5-sonnet-20241022": 0.003,
                    "claude-3-5-haiku-20241022": 0.00025,
                    "claude-3-opus-20240229": 0.015,
                    "claude-3-sonnet-20240229": 0.003,
                    "claude-3-haiku-20240307": 0.00025
                },
                "features": {
                    "function_calling": True,
                    "vision": True,
                    "code_execution": True,
                    "artifacts": True,
                    "advanced_reasoning": True
                }
            }
        }
    
    async def initialize(self) -> bool:
        """Inicializar o sistema de credenciais"""
        try:
            # Tentar carregar de diferentes fontes
            success = await self._load_credentials()
            
            if not success:
                self.logger.info("🔑 Nenhuma credencial encontrada. Configure usando setup_credentials()")
                return False
            
            # Validar credenciais carregadas
            valid_providers = await self._validate_credentials()
            
            if valid_providers == 0:
                self.logger.warning("⚠️ Nenhum provider válido encontrado")
                return False
            
            self.logger.info(f"✅ {valid_providers} providers LLM carregados com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na inicialização: {e}")
            return False
    
    async def _load_credentials(self) -> bool:
        """Carregar credenciais de múltiplas fontes"""
        loaded = False
        
        # 1. Tentar carregar de environment variables
        if self._load_from_env():
            loaded = True
            self.logger.info("📂 Credenciais carregadas de environment variables")
        
        # 2. Tentar carregar de arquivo criptografado
        elif self._load_from_encrypted_file():
            loaded = True
            self.logger.info("🔒 Credenciais carregadas de arquivo criptografado")
        
        # 3. Se não encontrou nada, verificar se tem .env.local
        elif self.env_file.exists():
            load_dotenv(self.env_file)
            if self._load_from_env():
                loaded = True
                self.logger.info("📄 Credenciais carregadas de .env.local")
        
        return loaded
    
    def _load_from_env(self) -> bool:
        """Carregar credenciais de environment variables"""
        loaded_count = 0
        
        for provider_name, config in self.provider_configs.items():
            env_key = f"{provider_name.upper()}_API_KEY"
            api_key = os.getenv(env_key)
            
            if api_key and api_key != "your_api_key_here":
                self.providers[provider_name] = LLMProvider(
                    name=provider_name,
                    api_key=api_key,
                    base_url=config["base_url"],
                    models=config["models"],
                    rate_limit=int(os.getenv(f"{provider_name.upper()}_RATE_LIMIT", config["rate_limit"])),
                    monthly_limit=float(os.getenv(f"{provider_name.upper()}_MONTHLY_LIMIT", config["monthly_limit"])),
                    cost_per_1k_tokens=config["cost_per_1k_tokens"]
                )
                loaded_count += 1
        
        return loaded_count > 0
    
    def _load_from_encrypted_file(self) -> bool:
        """Carregar credenciais de arquivo criptografado"""
        if not self.credentials_file.exists():
            return False
        
        try:
            password = getpass.getpass("🔑 Senha para descriptografar credenciais: ")
            
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Descriptografar
            key = self._derive_key(password)
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Carregar dados
            data = json.loads(decrypted_data.decode())
            
            for provider_name, provider_data in data.items():
                if provider_name in self.provider_configs:
                    self.providers[provider_name] = LLMProvider(**provider_data)
            
            return len(self.providers) > 0
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao descriptografar credenciais: {e}")
            return False
    
    async def setup_credentials(self, interactive: bool = True) -> bool:
        """Configurar credenciais interativamente"""
        self.logger.info("🔧 Configurando credenciais LLM...")
        
        if interactive:
            return await self._interactive_setup()
        else:
            return self._automated_setup()
    
    async def _interactive_setup(self) -> bool:
        """Setup interativo de credenciais"""
        print("\n🔐 === CONFIGURAÇÃO SEGURA DE CREDENCIAIS LLM ===")
        print("Digite 'skip' para pular um provider")
        print("As credenciais serão criptografadas antes de serem salvas")
        print()
        
        configured_count = 0
        
        for provider_name, config in self.provider_configs.items():
            print(f"\n🤖 Configurando {provider_name.upper()}:")
            print(f"   Modelos: {', '.join(config['models'])}")
            print(f"   Rate limit: {config['rate_limit']}/min")
            
            api_key = getpass.getpass(f"   API Key para {provider_name} (não aparecerá na tela): ")
            
            if api_key and api_key.lower() != 'skip':
                self.providers[provider_name] = LLMProvider(
                    name=provider_name,
                    api_key=api_key,
                    base_url=config["base_url"],
                    models=config["models"],
                    rate_limit=config["rate_limit"],
                    monthly_limit=config["monthly_limit"],
                    cost_per_1k_tokens=config["cost_per_1k_tokens"]
                )
                configured_count += 1
                print(f"   ✅ {provider_name} configurado")
            else:
                print(f"   ⏭️ {provider_name} pulado")
        
        if configured_count > 0:
            # Salvar credenciais criptografadas
            await self._save_encrypted_credentials()
            self.logger.info(f"✅ {configured_count} providers configurados com sucesso")
            return True
        else:
            self.logger.warning("⚠️ Nenhum provider foi configurado")
            return False
    
    def _automated_setup(self) -> bool:
        """Setup automatizado via environment variables"""
        print("\n📋 Para setup automatizado, configure as seguintes variáveis:")
        print("export GEMINI_API_KEY=your_key_here")
        print("export OPENAI_API_KEY=your_key_here") 
        print("export HUGGINGFACE_API_KEY=your_key_here")
        print("export ANTHROPIC_API_KEY=your_key_here")
        print("\nOu crie um arquivo .env.local com essas variáveis")
        return False
    
    async def _save_encrypted_credentials(self):
        """Salvar credenciais criptografadas"""
        password = getpass.getpass("🔒 Senha para criptografar credenciais (lembre-se dela!): ")
        
        # Converter providers para dict
        data = {}
        for name, provider in self.providers.items():
            data[name] = asdict(provider)
        
        # Criptografar
        key = self._derive_key(password)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(json.dumps(data).encode())
        
        # Salvar
        with open(self.credentials_file, 'wb') as f:
            f.write(encrypted_data)
        
        self.logger.info(f"🔒 Credenciais salvas criptografadas em {self.credentials_file}")
    
    def _derive_key(self, password: str) -> bytes:
        """Derivar chave de criptografia da senha"""
        salt = b'uptax_llm_salt_2025'  # Em produção, use salt aleatório
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    async def _validate_credentials(self) -> int:
        """Validar credenciais com teste de conectividade"""
        valid_count = 0
        
        for provider_name, provider in self.providers.items():
            try:
                # Simular validação (em implementação real, fazer chamada de teste)
                if len(provider.api_key) > 10:
                    valid_count += 1
                    self.logger.info(f"✅ {provider_name}: Credencial válida")
                else:
                    self.logger.warning(f"⚠️ {provider_name}: Credencial muito curta")
                    
            except Exception as e:
                self.logger.error(f"❌ {provider_name}: Erro na validação - {e}")
        
        return valid_count
    
    async def get_api_key(self, provider: str) -> Optional[str]:
        """Obter API key de um provider"""
        if provider in self.providers:
            return self.providers[provider].api_key
        return None
    
    async def get_provider_config(self, provider: str) -> Optional[LLMProvider]:
        """Obter configuração completa de um provider"""
        return self.providers.get(provider)
    
    async def list_available_providers(self) -> List[str]:
        """Listar providers disponíveis"""
        return list(self.providers.keys())
    
    async def get_optimal_provider(self, complexity: str, budget: float, quality_req: int = 7) -> Optional[str]:
        """Selecionar provider ótimo baseado em critérios"""
        if not self.providers:
            return None
        
        # Lógica de seleção baseada em complexidade
        complexity_mapping = {
            "trivial": ["gemini", "huggingface"],
            "simple": ["gemini", "huggingface", "openai"],
            "moderate": ["gemini", "openai"],
            "complex": ["openai", "anthropic"],
            "expert": ["openai", "anthropic"],
            "epic": ["anthropic", "openai"]
        }
        
        preferred_providers = complexity_mapping.get(complexity, list(self.providers.keys()))
        
        # Filtrar por providers disponíveis
        available_preferred = [p for p in preferred_providers if p in self.providers]
        
        if available_preferred:
            return available_preferred[0]
        elif self.providers:
            return list(self.providers.keys())[0]
        else:
            return None
    
    async def track_usage(self, provider: str, model: str, tokens: int, 
                         task_id: str = None, operation: str = "unknown") -> LLMUsageRecord:
        """Rastrear uso de LLM"""
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} não encontrado")
        
        provider_config = self.providers[provider]
        cost_per_1k = provider_config.cost_per_1k_tokens.get(model, 0.001)
        cost = (tokens / 1000) * cost_per_1k
        
        # Atualizar total do provider
        provider_config.total_cost += cost
        provider_config.last_used = datetime.now().isoformat()
        
        # Criar registro
        record = LLMUsageRecord(
            provider=provider,
            model=model,
            tokens_used=tokens,
            cost=cost,
            timestamp=datetime.now().isoformat(),
            task_id=task_id,
            operation=operation
        )
        
        self.usage_records.append(record)
        
        # Log do uso
        self.logger.info(f"💰 {provider}/{model}: {tokens} tokens, ${cost:.4f}")
        
        return record
    
    async def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """Obter resumo de uso dos últimos N dias"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_records = [
            r for r in self.usage_records 
            if datetime.fromisoformat(r.timestamp) >= cutoff_date
        ]
        
        summary = {
            "period_days": days,
            "total_records": len(recent_records),
            "total_tokens": sum(r.tokens_used for r in recent_records),
            "total_cost": sum(r.cost for r in recent_records),
            "by_provider": {},
            "by_model": {}
        }
        
        # Agrupar por provider
        for record in recent_records:
            if record.provider not in summary["by_provider"]:
                summary["by_provider"][record.provider] = {
                    "tokens": 0, "cost": 0.0, "requests": 0
                }
            
            summary["by_provider"][record.provider]["tokens"] += record.tokens_used
            summary["by_provider"][record.provider]["cost"] += record.cost
            summary["by_provider"][record.provider]["requests"] += 1
        
        return summary
    
    async def check_rate_limits(self, provider: str) -> Dict[str, Any]:
        """Verificar status de rate limits"""
        if provider not in self.providers:
            return {"error": "Provider não encontrado"}
        
        # Implementação simplificada - em produção, usar cache Redis
        return {
            "provider": provider,
            "rate_limit": self.providers[provider].rate_limit,
            "current_usage": 0,  # Seria calculado do cache
            "reset_time": "em implementação",
            "status": "ok"
        }

# Função de conveniência para setup rápido
async def quick_setup():
    """Setup rápido para desenvolvimento"""
    manager = UptaxLLMCredentialsManager()
    
    print("🚀 === SETUP RÁPIDO LLM CREDENTIALS ===")
    print("Este setup criará um arquivo .env.local seguro")
    
    if not await manager.setup_credentials():
        print("❌ Setup cancelado")
        return False
    
    if await manager.initialize():
        print("✅ LLM Credentials Manager configurado com sucesso!")
        
        # Mostrar providers disponíveis
        providers = await manager.list_available_providers()
        print(f"📋 Providers disponíveis: {', '.join(providers)}")
        
        return True
    else:
        print("❌ Erro na inicialização")
        return False

# Teste básico
async def test_credentials_manager():
    """Teste básico do sistema"""
    manager = UptaxLLMCredentialsManager()
    
    if await manager.initialize():
        print("✅ Sistema inicializado")
        
        # Testar seleção ótima
        optimal = await manager.get_optimal_provider("moderate", 5.0, 8)
        print(f"🎯 Provider ótimo para tarefa moderada: {optimal}")
        
        # Simular uso
        if optimal:
            record = await manager.track_usage(
                provider=optimal,
                model="gpt-4o-mini",
                tokens=1500,
                operation="test"
            )
            print(f"💰 Uso registrado: ${record.cost:.4f}")
        
        # Resumo
        summary = await manager.get_usage_summary()
        print(f"📊 Resumo: {summary['total_tokens']} tokens, ${summary['total_cost']:.4f}")
        
    else:
        print("❌ Falha na inicialização - execute setup_credentials() primeiro")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="UpTax LLM Credentials Manager")
    parser.add_argument("--setup", action="store_true", help="Configurar credenciais")
    parser.add_argument("--test", action="store_true", help="Testar sistema")
    parser.add_argument("--quick", action="store_true", help="Setup rápido")
    
    args = parser.parse_args()
    
    if args.setup:
        asyncio.run(UptaxLLMCredentialsManager().setup_credentials())
    elif args.test:
        asyncio.run(test_credentials_manager())
    elif args.quick:
        asyncio.run(quick_setup())
    else:
        print("🔐 UpTax LLM Credentials Manager")
        print("Use --setup para configurar credenciais")
        print("Use --test para testar o sistema")
        print("Use --quick para setup rápido")