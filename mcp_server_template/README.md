# 🛠️ MCP Server Template

## 📋 Visão Geral

Template padronizado para criação de servidores MCP (Model Context Protocol) com suporte híbrido para:
- **STDIO**: Integração com Claude Desktop
- **HTTP**: Integração com N8N, Zapier, Microsoft Copilot
- **SSE**: Server-Sent Events para streaming em tempo real

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.9+
- FastAPI
- Uvicorn

### Instalação
```bash
pip install -r requirements.txt
```

### Execução
```bash
# Modo STDIO (Claude Desktop)
python server.py --mode stdio

# Modo HTTP (N8N, Zapier)
python server.py --mode http --port 3000

# Modo debug
python server.py --mode http --debug
```

## 🏗️ Estrutura

```
mcp_server_template/
├── src/
│   ├── __init__.py
│   ├── server.py              # Servidor híbrido principal
│   ├── tools/                 # Ferramentas MCP
│   │   ├── __init__.py
│   │   ├── base.py           # Classe base para ferramentas
│   │   └── example_tool.py   # Ferramenta de exemplo
│   ├── client/               # Cliente para API externa
│   │   ├── __init__.py
│   │   └── api_client.py     # Cliente HTTP
│   └── utils/                # Utilitários
│       ├── __init__.py
│       ├── logger.py         # Logger configurado
│       └── validators.py     # Validadores
├── tests/
│   ├── __init__.py
│   ├── test_server.py        # Testes do servidor
│   └── test_tools.py         # Testes das ferramentas
├── docs/
│   ├── api.md                # Documentação da API
│   ├── tools.md              # Documentação das ferramentas
│   └── deployment.md         # Guia de deploy
├── examples/
│   ├── n8n_integration.json  # Exemplo N8N
│   ├── zapier_webhook.js     # Exemplo Zapier
│   └── claude_config.json    # Exemplo Claude Desktop
├── requirements.txt          # Dependências
├── Dockerfile               # Container Docker
└── README.md               # Este arquivo
```

## 📚 Documentação

### Ferramentas
- [Documentação das Ferramentas](docs/tools.md)
- [API Reference](docs/api.md)
- [Guia de Deploy](docs/deployment.md)

### Exemplos
- [Integração N8N](examples/n8n_integration.json)
- [Webhook Zapier](examples/zapier_webhook.js)
- [Configuração Claude](examples/claude_config.json)

## 🔧 Customização

### Adicionando Nova Ferramenta
1. Crie arquivo em `src/tools/nova_ferramenta.py`
2. Herde de `BaseTool`
3. Implemente métodos obrigatórios
4. Registre no servidor

### Exemplo:
```python
from src.tools.base import BaseTool

class NovaFerramenta(BaseTool):
    name = "nova_ferramenta"
    description = "Descrição da ferramenta"
    
    def get_input_schema(self):
        return {
            "type": "object",
            "properties": {
                "param": {"type": "string", "description": "Parâmetro"}
            }
        }
    
    async def execute(self, arguments):
        # Implementação da ferramenta
        return {"result": "sucesso"}
```

## 🧪 Testes

```bash
# Executar todos os testes
python -m pytest tests/ -v

# Testes com cobertura
python -m pytest tests/ --cov=src --cov-report=html

# Teste específico
python -m pytest tests/test_server.py -v
```

## 📦 Deploy

### Docker
```bash
# Build
docker build -t mcp-server .

# Run
docker run -p 3000:3000 mcp-server --mode http
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: mcp-server:latest
        ports:
        - containerPort: 3000
        args: ["--mode", "http", "--port", "3000"]
```

## 📝 Contribuindo

1. Fork o projeto
2. Crie branch para feature (`git checkout -b feature/nova-feature`)
3. Commit as mudanças (`git commit -am 'Add nova feature'`)
4. Push para branch (`git push origin feature/nova-feature`)
5. Crie Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- 📧 Email: suporte@uptax.com
- 📝 Issues: [GitHub Issues](https://github.com/kleberdossantosribeiro/omie-mcp-ecosystem/issues)
- 📖 Wiki: [GitHub Wiki](https://github.com/kleberdossantosribeiro/omie-mcp-ecosystem/wiki)

---

**Template criado com ❤️ pela equipe Uptax**