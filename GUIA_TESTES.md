# 🧪 Guia Completo de Testes - Omie MCP

## 🎯 Estratégias de Teste

### 1. **Teste Rápido da Conexão** (Imediato)
```bash
# Testar apenas consultas (sem rate limit)
python -c "
import asyncio
from omie_client_final_corrigido import OmieClientFinalCorrigido

async def teste_rapido():
    client = OmieClientFinalCorrigido()
    
    # Teste conexão
    if await client.teste_conexao():
        print('✅ API funcionando!')
        
        # Listar primeiros clientes
        clientes = await client.listar_clientes()
        print(f'📊 Total: {clientes.get(\"total_de_registros\", 0)} clientes')
        
        # Listar categorias
        categorias = await client.listar_categorias()
        print(f'📋 Total: {categorias.get(\"total_de_registros\", 0)} categorias')
    else:
        print('❌ Problemas na conexão')

asyncio.run(teste_rapido())
"
```

### 2. **Teste do Servidor MCP** (Backend)
```bash
# Testar servidor MCP stdio
python omie_mcp_server.py

# Ou testar servidor HTTP
python omie_http_server.py
```

### 3. **Teste do Frontend** (Dashboard)
```bash
# Navegar para o dashboard
cd omie-dashboard-v2

# Abrir no navegador
open index.html
# ou
python -m http.server 8000
# Depois abrir: http://localhost:8000
```

## 🛠️ Testes Específicos

### A. **Teste de Consultas** (Sem Rate Limit)
```python
# teste_consultas.py
import asyncio
from omie_client_final_corrigido import OmieClientFinalCorrigido

async def testar_consultas():
    client = OmieClientFinalCorrigido()
    
    testes = [
        ("Clientes", client.listar_clientes),
        ("Categorias", client.listar_categorias),
        ("Departamentos", client.listar_departamentos),
        ("Contas a Pagar", client.listar_contas_pagar),
        ("Contas a Receber", client.listar_contas_receber),
    ]
    
    for nome, metodo in testes:
        try:
            resultado = await metodo()
            total = resultado.get('total_de_registros', 0)
            print(f"✅ {nome}: {total} registros")
        except Exception as e:
            print(f"❌ {nome}: {str(e)}")

asyncio.run(testar_consultas())
```

### B. **Teste de Criação** (Após Rate Limit)
```python
# teste_criacao.py
import asyncio
from omie_client_final_corrigido import OmieClientFinalCorrigido

async def testar_criacao():
    client = OmieClientFinalCorrigido()
    
    # Teste cliente
    dados_cliente = {
        "razao_social": "TESTE FINAL LTDA",
        "nome_fantasia": "Teste Final",
        "email": "teste@final.com"
    }
    
    try:
        resultado = await client.incluir_cliente(dados_cliente)
        print(f"✅ Cliente criado: {resultado}")
    except Exception as e:
        if "Rate limit" in str(e):
            print("⏳ Rate limit ativo - aguarde")
        else:
            print(f"❌ Erro: {e}")

asyncio.run(testar_criacao())
```

### C. **Teste Integration End-to-End**
```bash
# Criar script de teste completo
cat > teste_completo.py << 'EOF'
#!/usr/bin/env python3
import asyncio
import json
from omie_client_final_corrigido import OmieClientFinalCorrigido

async def teste_completo():
    print("🧪 TESTE COMPLETO DA APLICAÇÃO")
    print("="*50)
    
    client = OmieClientFinalCorrigido()
    
    # 1. Testar conexão
    print("1. Testando conexão...")
    if not await client.teste_conexao():
        print("❌ Falha na conexão")
        return
    
    # 2. Testar consultas
    print("\n2. Testando consultas...")
    try:
        clientes = await client.listar_clientes({"pagina": 1, "registros_por_pagina": 5})
        print(f"✅ Clientes: {len(clientes.get('clientes_cadastro', []))} encontrados")
        
        categorias = await client.listar_categorias({"pagina": 1, "registros_por_pagina": 5})
        print(f"✅ Categorias: {len(categorias.get('categoria_cadastro', []))} encontradas")
        
    except Exception as e:
        print(f"❌ Erro nas consultas: {e}")
        return
    
    # 3. Testar criação (se não houver rate limit)
    print("\n3. Testando criação...")
    try:
        resultado = await client.teste_cliente_completo()
        print("✅ Cliente de teste criado com sucesso!")
        print(f"🆔 ID: {resultado.get('codigo_cliente_omie', 'N/A')}")
        
    except Exception as e:
        if "Rate limit" in str(e) or "425" in str(e):
            print("⏳ Rate limit ativo - criação adiada")
        else:
            print(f"❌ Erro na criação: {e}")
    
    print("\n🎉 TESTE COMPLETO FINALIZADO!")

if __name__ == "__main__":
    asyncio.run(teste_completo())
EOF

python teste_completo.py
```

## 🌐 Teste do Frontend

### 1. **Servidor Local**
```bash
# Opção 1: Servidor Python
cd omie-dashboard-v2
python -m http.server 8000

# Opção 2: Servidor Node.js (se instalado)
npx http-server -p 8000

# Opção 3: Apenas abrir arquivo
open index.html
```

### 2. **Teste das Funcionalidades**
```bash
# Checklist de teste do frontend:
# ✅ Tela de boas-vindas carrega
# ✅ Botão "Configurar Nova Aplicação" funciona
# ✅ Formulário de empresa abre
# ✅ Campos de CNPJ/telefone funcionam
# ✅ Navegação entre telas funciona
# ✅ Layout responsivo (mobile/tablet)
# ✅ Densidade 100% (não requer zoom)
```

## 🔧 Testes de Integração

### A. **Servidor MCP + Cliente**
```bash
# Terminal 1: Iniciar servidor MCP
python omie_mcp_server.py

# Terminal 2: Testar cliente
python -c "
import asyncio
from src.client.omie_client_fixed import omie_client_fixed

async def teste_mcp():
    resultado = await omie_client_fixed.consultar_clientes({'pagina': 1})
    print(f'MCP funcionando: {len(resultado.get(\"clientes_cadastro\", []))} clientes')

asyncio.run(teste_mcp())
"
```

### B. **Servidor HTTP + Frontend**
```bash
# Terminal 1: Iniciar servidor HTTP
python omie_http_server.py

# Terminal 2: Testar endpoints
curl -X POST http://localhost:8000/geral/clientes/ \
  -H "Content-Type: application/json" \
  -d '{"call": "ListarClientes", "param": [{"pagina": 1}]}'
```

## 📊 Testes de Performance

### 1. **Rate Limit Test**
```python
# teste_rate_limit.py
import asyncio
import time
from omie_client_final_corrigido import OmieClientFinalCorrigido

async def teste_rate_limit():
    client = OmieClientFinalCorrigido()
    
    print("🔄 Testando rate limiting...")
    
    for i in range(5):
        inicio = time.time()
        
        try:
            await client.listar_clientes({"pagina": 1, "registros_por_pagina": 1})
            fim = time.time()
            print(f"✅ Request {i+1}: {fim-inicio:.2f}s")
            
        except Exception as e:
            print(f"❌ Request {i+1}: {e}")
            break

asyncio.run(teste_rate_limit())
```

### 2. **Stress Test**
```python
# teste_stress.py
import asyncio
import time
from omie_client_final_corrigido import OmieClientFinalCorrigido

async def teste_stress():
    client = OmieClientFinalCorrigido()
    
    print("💪 Teste de stress (10 requests simultâneas)...")
    
    async def request_individual(i):
        try:
            resultado = await client.listar_clientes({"pagina": 1, "registros_por_pagina": 1})
            return f"✅ Request {i}: OK"
        except Exception as e:
            return f"❌ Request {i}: {e}"
    
    # Executar 10 requests paralelas
    tasks = [request_individual(i) for i in range(10)]
    resultados = await asyncio.gather(*tasks)
    
    for resultado in resultados:
        print(resultado)

asyncio.run(teste_stress())
```

## 🚀 Comandos Rápidos

```bash
# Teste rápido completo
python teste_completo.py

# Teste apenas consultas
python teste_consultas.py

# Teste frontend local
cd omie-dashboard-v2 && python -m http.server 8000

# Teste servidor MCP
python omie_mcp_server.py

# Teste servidor HTTP
python omie_http_server.py

# Verificar rate limit
python -c "
from omie_client_final_corrigido import OmieClientFinalCorrigido
client = OmieClientFinalCorrigido()
if client.rate_limit_until:
    print(f'Rate limit até: {client.rate_limit_until}')
else:
    print('Sem rate limit ativo')
"
```

## 🎯 Próximos Passos

1. **Agora** - Testar consultas (funcionam)
2. **Em ~20 minutos** - Testar criações (após rate limit)
3. **Frontend** - Testar interface completa
4. **Integração** - Conectar frontend + backend

## 💡 Dicas Importantes

- **Consultas**: Sempre funcionam, sem rate limit
- **Criações**: Aguardar fim do rate limit
- **Frontend**: Independente do backend
- **Rate limit**: ~20 minutos restantes
- **Documentos**: Sempre usar válidos (CNPJ/CPF)