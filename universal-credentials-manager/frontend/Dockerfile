# Dockerfile para Frontend Next.js
FROM node:18-alpine

# Configurar variáveis de ambiente
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Criar diretório de trabalho
WORKDIR /app

# Copiar package.json e package-lock.json
COPY package*.json ./

# Instalar dependências
RUN npm ci

# Copiar código fonte
COPY . .

# Expor porta
EXPOSE 3000

# Comando para iniciar em modo desenvolvimento
CMD ["npm", "run", "dev"]