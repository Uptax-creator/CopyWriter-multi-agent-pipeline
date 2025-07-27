# 🐘 EXEMPLO PRÁTICO - MCP POSTGRESQL UPTAX

## 📝 WORKFLOW COMPLETO DE CRUD

### **1. CRIAR NOVA TAREFA (CREATE)**
```json
// Tool: create_task
{
  "title": "Integrar Omie com N8N", 
  "description": "Criar workflow automatizado para sincronização de dados entre Omie e sistema interno via N8N",
  "priority": "high",
  "assigned_service": "omie_mcp",
  "assigned_user": "dev@uptax.com",
  "estimated_hours": 12,
  "due_date": "2025-02-15T18:00:00Z",
  "ai_generated": false,
  "metadata": {
    "client": "Cliente Premium",
    "complexity": "medium",
    "tags": ["integration", "omie", "n8n"]
  }
}

// Resposta:
{
  "success": true,
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Integrar Omie com N8N",
    "status": "pending",
    "created_at": "2025-01-26T10:30:00Z"
  }
}
```

### **2. ADICIONAR SUBTAREFAS**
```json
// Tool: create_subtask
{
  "parent_task_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Configurar autenticação Omie API",
  "description": "Setup OAuth2 e tokens de acesso"
}

// Tool: create_subtask  
{
  "parent_task_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Criar workflow N8N",
  "description": "Desenhar fluxo de sincronização automática"
}
```

### **3. ATUALIZAR PROGRESSO (UPDATE)**
```json
// Tool: update_task
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "in_progress",
  "progress": 25,
  "actual_hours": 3,
  "add_log": true
}

// Resposta:
{
  "success": true,
  "task": {
    "id": "123e4567-e89b-12d3-a456-426614174000", 
    "status": "in_progress",
    "progress": 25,
    "updated_at": "2025-01-26T14:15:00Z"
  }
}
```

### **4. ADICIONAR COMENTÁRIOS**
```json
// Tool: add_task_comment
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "API Omie configurada com sucesso. Iniciando desenvolvimento do workflow N8N.",
  "type": "status_change",
  "author": "dev@uptax.com",
  "metadata": {
    "milestone": "auth_completed",
    "next_step": "n8n_workflow"
  }
}
```

### **5. CONSULTAS AVANÇADAS (READ)**

#### **5.1 Buscar Tarefas por Filtros:**
```json
// Tool: get_tasks
{
  "status": "in_progress",
  "assigned_service": "omie_mcp",
  "priority": "high",
  "limit": 10,
  "order_by": "updated_at",
  "order_direction": "desc"
}

// Resposta:
{
  "success": true,
  "tasks": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Integrar Omie com N8N",
      "status": "in_progress",
      "progress": 25,
      "assigned_service": "omie_mcp"
    }
  ],
  "count": 1,
  "total_count": 1
}
```

#### **5.2 Busca Full-Text:**
```json
// Tool: search_tasks
{
  "query": "omie integração API",
  "language": "portuguese",
  "limit": 5
}

// Resposta:
{
  "success": true,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Integrar Omie com N8N", 
      "relevance_score": 0.95,
      "description": "Criar workflow automatizado..."
    }
  ]
}
```

#### **5.3 Analytics por Serviço:**
```json
// Tool: get_task_analytics
{
  "group_by": "service",
  "metric": "completion_rate"
}

// Resposta:
{
  "success": true,
  "metrics": {
    "omie_mcp": {
      "total_tasks": 5,
      "completed": 3,
      "completion_rate": "60%"
    },
    "nibo_mcp": {
      "total_tasks": 3,
      "completed": 2, 
      "completion_rate": "67%"
    }
  }
}
```

#### **5.4 Query SQL Personalizada:**
```json
// Tool: execute_sql_query
{
  "query": "SELECT assigned_service, status, COUNT(*) as count FROM uptax_tasks WHERE created_at > '2025-01-01' GROUP BY assigned_service, status ORDER BY count DESC"
}

// Resposta:
{
  "success": true,
  "results": [
    {"assigned_service": "omie_mcp", "status": "completed", "count": 15},
    {"assigned_service": "omie_mcp", "status": "in_progress", "count": 8},
    {"assigned_service": "nibo_mcp", "status": "completed", "count": 12}
  ]
}
```

### **6. ATUALIZAÇÃO EM LOTE**
```json
// Tool: bulk_update_tasks
{
  "task_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "456e7890-e89b-12d3-a456-426614174001" 
  ],
  "updates": {
    "assigned_user": "senior@uptax.com",
    "priority": "urgent"
  },
  "add_bulk_log": true
}

// Resposta:
{
  "success": true,
  "updated": 2,
  "total": 2,
  "results": [
    {"task_id": "123e4567-e89b-12d3-a456-426614174000", "success": true},
    {"task_id": "456e7890-e89b-12d3-a456-426614174001", "success": true}
  ]
}
```

### **7. PREPARAR GITHUB SYNC**
```json
// Tool: prepare_github_sync
{
  "repository": "uptax-ai-platform/omie-mcp",
  "dry_run": false,
  "filter_service": "omie_mcp",
  "max_tasks": 10
}

// Resposta:
{
  "repository": "uptax-ai-platform/omie-mcp",
  "tasks_count": 3,
  "tasks": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Integrar Omie com N8N",
      "priority": "high"
    }
  ]
}
```

## ✅ **RESUMO DAS OPERAÇÕES CRUD**

| Operação | Tools Disponíveis | Exemplo |
|----------|------------------|---------|
| **CREATE** | `create_task`, `create_subtask`, `add_task_comment`, `create_task_dependency` | Criar tarefa, subtarefa, comentário |
| **READ** | `get_tasks`, `search_tasks`, `get_task_analytics`, `execute_sql_query` | Buscar, filtrar, analytics |
| **UPDATE** | `update_task`, `bulk_update_tasks` | Atualizar individual ou em lote |
| **DELETE** | Implícito via `status: "cancelled"` | Cancelar tarefa (soft delete) |

## 🚀 **VANTAGENS DO MCP POSTGRESQL**

- ✅ **CRUD Completo** via 11 ferramentas
- ✅ **Transações ACID** garantidas 
- ✅ **Full-text search** em português
- ✅ **Queries SQL** personalizadas
- ✅ **JSONB metadata** flexível
- ✅ **Logs automáticos** de mudanças
- ✅ **Bulk operations** eficientes
- ✅ **GitHub sync** integrado
- ✅ **Analytics avançadas** 
- ✅ **Pool de conexões** otimizado

O MCP PostgreSQL oferece funcionalidade completa de banco de dados através de uma interface MCP simples e poderosa!