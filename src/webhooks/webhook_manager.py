#!/usr/bin/env python3
"""
🔄 SISTEMA DE WEBHOOKS OMIE MCP
Processamento de eventos em tempo real e integrações bidirecionais
"""

import asyncio
import json
import hashlib
import hmac
import uuid
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
import uvicorn
import aiohttp
from pydantic import BaseModel

@dataclass
class WebhookEvent:
    """Evento de webhook"""
    event_id: str
    event_type: str
    source: str  # "omie", "mcp", "external"
    data: Dict[str, Any]
    timestamp: str
    signature: Optional[str] = None
    processed: bool = False
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class WebhookEndpoint:
    """Configuração de endpoint webhook"""
    endpoint_id: str
    name: str
    url: str
    secret: Optional[str]
    events: List[str]  # Tipos de eventos que este endpoint aceita
    active: bool = True
    retry_attempts: int = 3
    timeout_seconds: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class WebhookManager:
    """Gerenciador central de webhooks"""
    
    def __init__(self, config_file: str = "config/webhooks.json"):
        self.config_file = Path(config_file)
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        
        # Estatísticas
        self.stats = {
            "events_received": 0,
            "events_processed": 0,
            "events_failed": 0,
            "webhooks_sent": 0,
            "webhooks_failed": 0
        }
        
        # Carregar configuração
        self._load_config()
    
    def _load_config(self):
        """Carrega configuração de webhooks"""
        if not self.config_file.exists():
            self._create_default_config()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for endpoint_data in config.get("endpoints", []):
                endpoint = WebhookEndpoint(**endpoint_data)
                self.endpoints[endpoint.endpoint_id] = endpoint
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar config webhooks: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Cria configuração padrão"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        default_config = {
            "endpoints": [
                {
                    "endpoint_id": "n8n-integration",
                    "name": "N8N Workflow Integration",
                    "url": "http://localhost:5678/webhook/omie-mcp",
                    "secret": "omie-mcp-webhook-secret",
                    "events": ["conta_recebida", "conta_vencida", "cliente_cadastrado"],
                    "active": True,
                    "retry_attempts": 3,
                    "timeout_seconds": 30
                }
            ],
            "settings": {
                "max_queue_size": 1000,
                "batch_size": 10,
                "process_interval": 5
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuração padrão de webhooks criada: {self.config_file}")
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Gera assinatura HMAC para webhook"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def add_endpoint(self, name: str, url: str, events: List[str],
                          secret: str = None, **kwargs) -> str:
        """Adiciona novo endpoint webhook"""
        endpoint_id = str(uuid.uuid4())[:8]
        
        endpoint = WebhookEndpoint(
            endpoint_id=endpoint_id,
            name=name,
            url=url,
            secret=secret or f"webhook-{endpoint_id}",
            events=events,
            **kwargs
        )
        
        self.endpoints[endpoint_id] = endpoint
        self._save_config()
        
        return endpoint_id
    
    async def remove_endpoint(self, endpoint_id: str) -> bool:
        """Remove endpoint webhook"""
        if endpoint_id in self.endpoints:
            del self.endpoints[endpoint_id]
            self._save_config()
            return True
        return False
    
    def _save_config(self):
        """Salva configuração atual"""
        config = {
            "endpoints": [endpoint.to_dict() for endpoint in self.endpoints.values()],
            "settings": {
                "max_queue_size": 1000,
                "batch_size": 10,
                "process_interval": 5
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    async def register_event_handler(self, event_type: str, handler: Callable):
        """Registra handler para tipo específico de evento"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
    
    async def emit_event(self, event_type: str, data: Dict[str, Any], 
                        source: str = "mcp") -> str:
        """Emite evento para processamento"""
        event = WebhookEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            source=source,
            data=data,
            timestamp=datetime.now().isoformat()
        )
        
        await self.event_queue.put(event)
        self.stats["events_received"] += 1
        
        return event.event_id
    
    async def process_events(self):
        """Processa eventos da fila"""
        while True:
            try:
                # Processar eventos em batch
                events = []
                for _ in range(10):  # Batch de até 10 eventos
                    try:
                        event = await asyncio.wait_for(
                            self.event_queue.get(), 
                            timeout=1.0
                        )
                        events.append(event)
                    except asyncio.TimeoutError:
                        break
                
                if not events:
                    await asyncio.sleep(5)  # Wait se não há eventos
                    continue
                
                # Processar cada evento
                for event in events:
                    await self._process_single_event(event)
                
            except Exception as e:
                print(f"⚠️ Erro no processamento de eventos: {e}")
                await asyncio.sleep(5)
    
    async def _process_single_event(self, event: WebhookEvent):
        """Processa um único evento"""
        try:
            # Executar handlers locais
            if event.event_type in self.event_handlers:
                for handler in self.event_handlers[event.event_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        print(f"⚠️ Erro em handler {handler.__name__}: {e}")
            
            # Enviar para endpoints externos
            await self._send_to_endpoints(event)
            
            event.processed = True
            self.stats["events_processed"] += 1
            
        except Exception as e:
            print(f"⚠️ Erro ao processar evento {event.event_id}: {e}")
            event.retry_count += 1
            self.stats["events_failed"] += 1
            
            # Re-enfileirar se ainda pode tentar
            if event.retry_count < 3:
                await asyncio.sleep(event.retry_count * 5)  # Backoff exponencial
                await self.event_queue.put(event)
    
    async def _send_to_endpoints(self, event: WebhookEvent):
        """Envia evento para endpoints configurados"""
        for endpoint in self.endpoints.values():
            if (not endpoint.active or 
                event.event_type not in endpoint.events):
                continue
            
            await self._send_webhook(endpoint, event)
    
    async def _send_webhook(self, endpoint: WebhookEndpoint, event: WebhookEvent):
        """Envia webhook para endpoint específico"""
        try:
            payload = json.dumps(event.to_dict(), ensure_ascii=False)
            
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Event": event.event_type,
                "X-Webhook-ID": event.event_id,
                "X-Webhook-Timestamp": event.timestamp
            }
            
            # Adicionar assinatura se secret configurado
            if endpoint.secret:
                signature = self._generate_signature(payload, endpoint.secret)
                headers["X-Webhook-Signature"] = f"sha256={signature}"
            
            timeout = aiohttp.ClientTimeout(total=endpoint.timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    endpoint.url,
                    data=payload,
                    headers=headers
                ) as response:
                    if response.status < 400:
                        self.stats["webhooks_sent"] += 1
                        print(f"✅ Webhook enviado para {endpoint.name}: {event.event_type}")
                    else:
                        self.stats["webhooks_failed"] += 1
                        print(f"❌ Webhook falhou para {endpoint.name}: {response.status}")
        
        except Exception as e:
            self.stats["webhooks_failed"] += 1
            print(f"❌ Erro enviando webhook para {endpoint.name}: {e}")
    
    async def start_processing(self):
        """Inicia processamento de eventos"""
        if self.processing_task is None or self.processing_task.done():
            self.processing_task = asyncio.create_task(self.process_events())
            print("🔄 Processamento de webhooks iniciado")
    
    async def stop_processing(self):
        """Para processamento de eventos"""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            print("🛑 Processamento de webhooks parado")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de webhooks"""
        return {
            "statistics": self.stats.copy(),
            "endpoints": len(self.endpoints),
            "active_endpoints": len([e for e in self.endpoints.values() if e.active]),
            "queue_size": self.event_queue.qsize(),
            "processing_active": (
                self.processing_task is not None and 
                not self.processing_task.done()
            )
        }
    
    def list_endpoints(self) -> List[Dict[str, Any]]:
        """Lista todos os endpoints configurados"""
        return [endpoint.to_dict() for endpoint in self.endpoints.values()]

# ============================================================================
# SERVIDOR WEBHOOK RECEPTOR
# ============================================================================

class WebhookServer:
    """Servidor para receber webhooks externos"""
    
    def __init__(self, webhook_manager: WebhookManager, port: int = 8001):
        self.webhook_manager = webhook_manager
        self.port = port
        self.app = FastAPI(title="Omie MCP Webhook Server")
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura rotas do servidor"""
        
        @self.app.post("/webhook/omie")
        async def receive_omie_webhook(request: Request, background_tasks: BackgroundTasks):
            """Recebe webhooks do Omie"""
            try:
                body = await request.body()
                data = json.loads(body)
                
                # Processar webhook do Omie
                event_type = self._determine_omie_event_type(data)
                
                await self.webhook_manager.emit_event(
                    event_type=event_type,
                    data=data,
                    source="omie"
                )
                
                return {"status": "received", "event_type": event_type}
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/webhook/generic/{event_type}")
        async def receive_generic_webhook(event_type: str, request: Request):
            """Recebe webhooks genéricos"""
            try:
                body = await request.body()
                data = json.loads(body) if body else {}
                
                await self.webhook_manager.emit_event(
                    event_type=event_type,
                    data=data,
                    source="external"
                )
                
                return {"status": "received", "event_type": event_type}
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/webhook/status")
        async def webhook_status():
            """Status do sistema de webhooks"""
            return self.webhook_manager.get_stats()
        
        @self.app.get("/webhook/endpoints")
        async def list_endpoints():
            """Lista endpoints configurados"""
            return self.webhook_manager.list_endpoints()
    
    def _determine_omie_event_type(self, data: Dict[str, Any]) -> str:
        """Determina tipo de evento baseado nos dados do Omie"""
        # Lógica para identificar tipo de evento do Omie
        if "conta_receber" in str(data).lower():
            return "conta_recebida"
        elif "conta_pagar" in str(data).lower():
            return "conta_vencida"
        elif "cliente" in str(data).lower():
            return "cliente_cadastrado"
        else:
            return "evento_generico"
    
    async def start_server(self):
        """Inicia servidor webhook"""
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

# ============================================================================
# HANDLERS DE EVENTOS ESPECÍFICOS
# ============================================================================

async def handle_conta_recebida(event: WebhookEvent):
    """Handler para quando uma conta é recebida"""
    print(f"💰 Conta recebida: {event.data.get('valor', 'N/A')}")
    
    # Aqui seria implementada lógica específica:
    # - Atualizar cache de contas a receber
    # - Enviar notificação
    # - Atualizar dashboard
    
async def handle_conta_vencida(event: WebhookEvent):
    """Handler para quando uma conta vence"""
    print(f"⏰ Conta vencida: {event.data.get('numero_titulo', 'N/A')}")
    
    # Lógica para conta vencida:
    # - Disparar processo de cobrança
    # - Notificar responsável
    # - Atualizar relatórios

async def handle_cliente_cadastrado(event: WebhookEvent):
    """Handler para novo cliente"""
    print(f"👤 Novo cliente: {event.data.get('nome', 'N/A')}")
    
    # Lógica para novo cliente:
    # - Invalidar cache de clientes
    # - Enviar email de boas-vindas
    # - Atualizar estatísticas

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

async def main():
    """Função principal para teste do sistema de webhooks"""
    # Criar gerenciador de webhooks
    webhook_manager = WebhookManager()
    
    # Registrar handlers
    await webhook_manager.register_event_handler("conta_recebida", handle_conta_recebida)
    await webhook_manager.register_event_handler("conta_vencida", handle_conta_vencida)
    await webhook_manager.register_event_handler("cliente_cadastrado", handle_cliente_cadastrado)
    
    # Iniciar processamento
    await webhook_manager.start_processing()
    
    # Criar servidor webhook
    webhook_server = WebhookServer(webhook_manager)
    
    print("🔄 Sistema de Webhooks Omie MCP iniciado")
    print(f"🌐 Servidor webhook: http://localhost:8001")
    print("📊 Status: /webhook/status")
    print("📋 Endpoints: /webhook/endpoints")
    
    try:
        # Simular alguns eventos para teste
        await webhook_manager.emit_event(
            "conta_recebida",
            {"valor": 1500.00, "cliente": "Empresa ABC"}
        )
        
        await webhook_manager.emit_event(
            "conta_vencida", 
            {"numero_titulo": "DUP001", "valor": 2500.00}
        )
        
        # Iniciar servidor
        await webhook_server.start_server()
        
    except KeyboardInterrupt:
        await webhook_manager.stop_processing()
        print("🛑 Sistema de webhooks parado")

if __name__ == "__main__":
    asyncio.run(main())