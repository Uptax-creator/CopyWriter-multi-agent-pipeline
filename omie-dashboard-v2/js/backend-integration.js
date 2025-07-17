/**
 * Integração com Backend
 * Gerencia as conexões com APIs do backend
 */

class BackendIntegration {
    constructor() {
        this.baseURL = this.getBaseURL();
        this.timeout = 30000; // 30 segundos
        this.retryAttempts = 3;
        this.init();
    }

    init() {
        console.log('🔌 Inicializando integração com backend');
        console.log('🌐 Base URL:', this.baseURL);
        
        // Testar conectividade
        this.healthCheck();
    }

    getBaseURL() {
        // Detectar ambiente
        const hostname = window.location.hostname;
        
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8001'; // Servidor local FastAPI
        } else if (hostname.includes('staging')) {
            return 'https://staging-api.omie-tenant-manager.com';
        } else {
            return 'https://api.omie-tenant-manager.com';
        }
    }

    async healthCheck() {
        try {
            const response = await this.makeRequest('/health', 'GET');
            console.log('✅ Backend conectado:', response);
            return response;
        } catch (error) {
            console.warn('⚠️ Backend não disponível:', error.message);
            return { status: 'offline', error: error.message };
        }
    }

    // ===============================
    // MÉTODOS HTTP
    // ===============================

    async makeRequest(endpoint, method = 'GET', data = null, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...this.getAuthHeaders(),
                ...options.headers
            },
            timeout: this.timeout,
            ...options
        };

        if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await this.fetchWithTimeout(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('❌ Erro na requisição:', error);
            throw error;
        }
    }

    async fetchWithTimeout(url, config) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url, {
                ...config,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }

    getAuthHeaders() {
        const token = securityManager?.getSecureToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    // ===============================
    // AUTENTICAÇÃO
    // ===============================

    async login(email, password) {
        try {
            const response = await this.makeRequest('/auth/login', 'POST', {
                email,
                password
            });

            if (response.token) {
                // Armazenar token de forma segura
                securityManager?.storeTokenSecurely(response.token);
                
                // Armazenar dados do usuário
                localStorage.setItem('user_data', JSON.stringify(response.user));
                
                return response;
            }

            throw new Error('Token não recebido');
        } catch (error) {
            console.error('❌ Erro no login:', error);
            throw error;
        }
    }

    async register(userData) {
        try {
            const response = await this.makeRequest('/auth/register', 'POST', userData);
            return response;
        } catch (error) {
            console.error('❌ Erro no registro:', error);
            throw error;
        }
    }

    async logout() {
        try {
            await this.makeRequest('/auth/logout', 'POST');
            
            // Limpar dados locais
            securityManager?.clearSecureToken();
            localStorage.removeItem('user_data');
            localStorage.removeItem('current_company');
            
            return { success: true };
        } catch (error) {
            console.error('❌ Erro no logout:', error);
            // Mesmo com erro, limpar dados locais
            securityManager?.clearSecureToken();
            return { success: false, error: error.message };
        }
    }

    // ===============================
    // EMPRESAS
    // ===============================

    async getUserCompanies() {
        try {
            const response = await this.makeRequest('/companies', 'GET');
            return response;
        } catch (error) {
            console.error('❌ Erro ao buscar empresas:', error);
            throw error;
        }
    }

    async createCompany(companyData) {
        try {
            const response = await this.makeRequest('/companies', 'POST', companyData);
            return response;
        } catch (error) {
            console.error('❌ Erro ao criar empresa:', error);
            throw error;
        }
    }

    async updateCompany(companyId, companyData) {
        try {
            const response = await this.makeRequest(`/companies/${companyId}`, 'PUT', companyData);
            return response;
        } catch (error) {
            console.error('❌ Erro ao atualizar empresa:', error);
            throw error;
        }
    }

    // ===============================
    // APLICAÇÕES
    // ===============================

    async getApplications() {
        try {
            const response = await this.makeRequest('/applications', 'GET');
            return response;
        } catch (error) {
            console.error('❌ Erro ao buscar aplicações:', error);
            throw error;
        }
    }

    async createApplication(appData) {
        try {
            const response = await this.makeRequest('/applications', 'POST', appData);
            return response;
        } catch (error) {
            console.error('❌ Erro ao criar aplicação:', error);
            throw error;
        }
    }

    async getCompanyApplications(companyId) {
        try {
            const response = await this.makeRequest(`/companies/${companyId}/applications`, 'GET');
            return response;
        } catch (error) {
            console.error('❌ Erro ao buscar aplicações da empresa:', error);
            throw error;
        }
    }

    async configureCompanyApplication(companyId, appId, credentials) {
        try {
            const response = await this.makeRequest(
                `/companies/${companyId}/applications/${appId}/configure`, 
                'POST', 
                credentials
            );
            return response;
        } catch (error) {
            console.error('❌ Erro ao configurar aplicação:', error);
            throw error;
        }
    }

    async testApplicationConnection(companyId, appId) {
        try {
            const response = await this.makeRequest(
                `/companies/${companyId}/applications/${appId}/test-connection`, 
                'POST'
            );
            return response;
        } catch (error) {
            console.error('❌ Erro ao testar conexão:', error);
            throw error;
        }
    }

    // ===============================
    // OMIE MCP INTEGRATION
    // ===============================

    async getOmieClients(companyId) {
        try {
            const response = await this.makeRequest(
                `/companies/${companyId}/omie/clients`, 
                'GET'
            );
            return response;
        } catch (error) {
            console.error('❌ Erro ao buscar clientes Omie:', error);
            throw error;
        }
    }

    async createOmieClient(companyId, clientData) {
        try {
            const response = await this.makeRequest(
                `/companies/${companyId}/omie/clients`, 
                'POST', 
                clientData
            );
            return response;
        } catch (error) {
            console.error('❌ Erro ao criar cliente Omie:', error);
            throw error;
        }
    }

    async getOmieProducts(companyId) {
        try {
            const response = await this.makeRequest(
                `/companies/${companyId}/omie/products`, 
                'GET'
            );
            return response;
        } catch (error) {
            console.error('❌ Erro ao buscar produtos Omie:', error);
            throw error;
        }
    }

    // ===============================
    // VALIDAÇÕES
    // ===============================

    async validateEmail(email) {
        try {
            const response = await this.makeRequest('/auth/validate-email', 'POST', { email });
            return response;
        } catch (error) {
            console.error('❌ Erro ao validar email:', error);
            throw error;
        }
    }

    async validateCNPJ(cnpj) {
        try {
            const response = await this.makeRequest('/empresas/validate-cnpj', 'POST', { cnpj });
            return response;
        } catch (error) {
            console.error('❌ Erro ao validar CNPJ:', error);
            throw error;
        }
    }

    // ===============================
    // USUÁRIOS E CONVITES
    // ===============================

    async inviteUser(companyId, inviteData) {
        try {
            const response = await this.makeRequest(
                `/companies/${companyId}/invite`, 
                'POST', 
                inviteData
            );
            return response;
        } catch (error) {
            console.error('❌ Erro ao enviar convite:', error);
            throw error;
        }
    }

    async getCompanyUsers(companyId) {
        try {
            const response = await this.makeRequest(
                `/companies/${companyId}/users`, 
                'GET'
            );
            return response;
        } catch (error) {
            console.error('❌ Erro ao buscar usuários da empresa:', error);
            throw error;
        }
    }

    // ===============================
    // DASHBOARD E ESTATÍSTICAS
    // ===============================

    async getDashboardStats(companyId) {
        try {
            const response = await this.makeRequest(
                `/companies/${companyId}/dashboard`, 
                'GET'
            );
            return response;
        } catch (error) {
            console.error('❌ Erro ao buscar estatísticas:', error);
            throw error;
        }
    }

    async getActivityLogs(companyId, limit = 10) {
        try {
            const response = await this.makeRequest(
                `/companies/${companyId}/logs?limit=${limit}`, 
                'GET'
            );
            return response;
        } catch (error) {
            console.error('❌ Erro ao buscar logs:', error);
            throw error;
        }
    }

    // ===============================
    // UTILITÁRIOS
    // ===============================

    async validateCNPJ(cnpj) {
        try {
            const response = await this.makeRequest(
                `/utils/validate-cnpj`, 
                'POST', 
                { cnpj }
            );
            return response;
        } catch (error) {
            console.error('❌ Erro ao validar CNPJ:', error);
            throw error;
        }
    }

    async searchCEP(cep) {
        try {
            const response = await this.makeRequest(
                `/utils/search-cep`, 
                'POST', 
                { cep }
            );
            return response;
        } catch (error) {
            console.error('❌ Erro ao buscar CEP:', error);
            throw error;
        }
    }

    // ===============================
    // RETRY MECHANISM
    // ===============================

    async makeRequestWithRetry(endpoint, method = 'GET', data = null, options = {}) {
        let lastError;
        
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const response = await this.makeRequest(endpoint, method, data, options);
                return response;
            } catch (error) {
                lastError = error;
                
                if (attempt === this.retryAttempts) {
                    throw error;
                }
                
                // Aguardar antes de tentar novamente
                const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
                await new Promise(resolve => setTimeout(resolve, delay));
                
                console.warn(`⚠️ Tentativa ${attempt} falhou, tentando novamente em ${delay}ms...`);
            }
        }
        
        throw lastError;
    }

    // ===============================
    // MODO OFFLINE
    // ===============================

    isOnline() {
        return navigator.onLine;
    }

    async waitForOnline() {
        return new Promise(resolve => {
            if (this.isOnline()) {
                resolve();
            } else {
                const handleOnline = () => {
                    window.removeEventListener('online', handleOnline);
                    resolve();
                };
                window.addEventListener('online', handleOnline);
            }
        });
    }

    // ===============================
    // CACHE SIMPLES
    // ===============================

    setCache(key, data, ttl = 300000) { // 5 minutos por padrão
        const cacheData = {
            data,
            timestamp: Date.now(),
            ttl
        };
        localStorage.setItem(`cache_${key}`, JSON.stringify(cacheData));
    }

    getCache(key) {
        try {
            const cached = localStorage.getItem(`cache_${key}`);
            if (!cached) return null;

            const cacheData = JSON.parse(cached);
            if (Date.now() - cacheData.timestamp > cacheData.ttl) {
                localStorage.removeItem(`cache_${key}`);
                return null;
            }

            return cacheData.data;
        } catch (error) {
            console.error('❌ Erro ao recuperar cache:', error);
            return null;
        }
    }

    clearCache(pattern = null) {
        const keys = Object.keys(localStorage);
        keys.forEach(key => {
            if (key.startsWith('cache_')) {
                if (!pattern || key.includes(pattern)) {
                    localStorage.removeItem(key);
                }
            }
        });
    }
}

// Instanciar globalmente
const backendIntegration = new BackendIntegration();

// Disponibilizar para debug
if (window.location.hostname === 'localhost') {
    window.backendIntegration = backendIntegration;
}

console.log('✅ Backend integration carregado com sucesso');