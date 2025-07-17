/**
 * Cliente da API - Comunicação com o backend
 */

class ApiClient {
    constructor() {
        this.baseURL = 'http://127.0.0.1:8003';
        this.token = localStorage.getItem('access_token');
    }

    // Headers padrão para requisições
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    // Método genérico para fazer requisições
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            showLoading(true);
            
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || `Erro ${response.status}`);
            }
            
            return data;
            
        } catch (error) {
            console.error('Erro na API:', error);
            
            // Se for um erro de fetch (rede), não mostrar alert duplicado
            if (error instanceof TypeError && error.message.includes('fetch')) {
                throw new Error('Erro de conexão com o servidor');
            }
            
            // Para outros erros, propagar sem mostrar alert aqui
            throw error;
            
        } finally {
            showLoading(false);
        }
    }

    // Métodos HTTP específicos
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // Autenticação
    async login(appKey, appSecret) {
        const data = await this.post('/auth/token', {
            app_key: appKey,
            app_secret: appSecret
        });
        
        this.token = data.access_token;
        localStorage.setItem('access_token', this.token);
        localStorage.setItem('app_key', appKey);
        
        return data;
    }

    logout() {
        this.token = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('app_key');
    }

    isAuthenticated() {
        return !!this.token;
    }

    // Health Check
    async healthCheck() {
        return this.get('/health');
    }

    // === APLICAÇÕES DO SISTEMA ===
    
    async createApplication(description, type) {
        return this.post('/aplicacoes/', {
            descricao: description,
            tipo: type
        });
    }

    async getApplications() {
        return this.get('/aplicacoes/');
    }

    async getApplication(id) {
        return this.get(`/aplicacoes/${id}`);
    }

    async updateApplication(id, data) {
        return this.put(`/aplicacoes/${id}`, data);
    }

    async deleteApplication(id) {
        return this.delete(`/aplicacoes/${id}`);
    }

    async rotateAppSecret(id) {
        return this.post(`/aplicacoes/${id}/rotate-secret`);
    }

    async getApplicationTypes() {
        return this.get('/aplicacoes/tipos');
    }

    // === APLICAÇÕES DOS CLIENTES ===
    
    async createClientApplication(data) {
        return this.post('/aplicacoes/cliente', data);
    }

    async getClientApplications(filters = {}) {
        const params = new URLSearchParams();
        
        Object.keys(filters).forEach(key => {
            if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
                params.append(key, filters[key]);
            }
        });
        
        const queryString = params.toString();
        const endpoint = queryString ? `/aplicacoes/cliente?${queryString}` : '/aplicacoes/cliente';
        
        return this.get(endpoint);
    }

    async updateClientApplication(id, data) {
        return this.put(`/aplicacoes/cliente/${id}`, data);
    }

    // === EMPRESAS ===
    
    async createCompany(data) {
        return this.post('/empresas/', data);
    }

    async getCompanies(filters = {}) {
        const params = new URLSearchParams();
        
        Object.keys(filters).forEach(key => {
            if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
                params.append(key, filters[key]);
            }
        });
        
        const queryString = params.toString();
        const endpoint = queryString ? `/empresas/?${queryString}` : '/empresas/';
        
        return this.get(endpoint);
    }

    async getCompany(id) {
        return this.get(`/empresas/${id}`);
    }

    async updateCompany(id, data) {
        return this.put(`/empresas/${id}`, data);
    }

    async deleteCompany(id) {
        return this.delete(`/empresas/${id}`);
    }

    async getCompanyUsers(id) {
        return this.get(`/empresas/${id}/usuarios`);
    }

    async getCompanyApplications(id) {
        return this.get(`/empresas/${id}/aplicacoes`);
    }

    // === USUÁRIOS ===
    
    async createUser(data) {
        return this.post('/usuarios/', data);
    }

    async getUsers(filters = {}) {
        const params = new URLSearchParams();
        
        Object.keys(filters).forEach(key => {
            if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
                params.append(key, filters[key]);
            }
        });
        
        const queryString = params.toString();
        const endpoint = queryString ? `/usuarios/?${queryString}` : '/usuarios/';
        
        return this.get(endpoint);
    }

    async getUser(id) {
        return this.get(`/usuarios/${id}`);
    }

    async updateUser(id, data) {
        return this.put(`/usuarios/${id}`, data);
    }

    async deleteUser(id) {
        return this.delete(`/usuarios/${id}`);
    }
}

// Instância global da API
const api = new ApiClient();

// Funções utilitárias
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.toggle('d-none', !show);
    }
}

function showAlert(message, type = 'info', duration = 5000) {
    // Remove alertas existentes
    const existingAlerts = document.querySelectorAll('.alert-floating');
    existingAlerts.forEach(alert => alert.remove());
    
    // Cria novo alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show alert-floating`;
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove após duração especificada
    if (duration > 0) {
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, duration);
    }
}

function formatCNPJ(cnpj) {
    if (!cnpj) return '';
    const cleanCNPJ = cnpj.replace(/\D/g, '');
    return cleanCNPJ.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatStatus(active) {
    if (active) {
        return '<span class="status-badge status-ativo">Ativo</span>';
    } else {
        return '<span class="status-badge status-inativo">Inativo</span>';
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copiado para a área de transferência!', 'success', 2000);
    }).catch(() => {
        showAlert('Erro ao copiar', 'danger', 2000);
    });
}