# Multi-stage build para otimização
FROM python:3.12-slim as builder

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar e instalar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage final
FROM python:3.12-slim

# Instalar dependências runtime mínimas
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash mcp

# Copiar ambiente virtual
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Configurar diretório de trabalho
WORKDIR /app
RUN chown -R mcp:mcp /app

# Copiar código fonte
COPY --chown=mcp:mcp omie_fastmcp_unified.py .
COPY --chown=mcp:mcp src/ src/
COPY --chown=mcp:mcp config/ config/

# Criar diretórios necessários
RUN mkdir -p cache logs && chown -R mcp:mcp cache logs

# Mudar para usuário não-root
USER mcp

# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV MCP_SERVER_TYPE=omie
ENV OMIE_MCP_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.path.append('/app'); from omie_fastmcp_unified import mcp; print('OK')" || exit 1

# Expor porta padrão
EXPOSE 8001

# Comando de inicialização
CMD ["python", "omie_fastmcp_unified.py"]