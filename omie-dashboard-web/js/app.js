/**
 * Aplicação Principal - Controlador principal do frontend
 */

class App {
    constructor() {
        this.currentSection = 'dashboard';
        this.init();
    }

    init() {
        // Aguardar carregamento completo do DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }

    initialize() {
        console.log('Omie Tenant Manager - Frontend iniciado');
        
        // Configurar eventos globais
        this.setupGlobalEvents();
        
        // Verificar autenticação inicial
        this.checkInitialAuth();
    }

    setupGlobalEvents() {
        // Interceptar cliques em links do menu
        document.addEventListener('click', (e) => {
            const link = e.target.closest('[onclick*="showSection"]');
            if (link) {
                e.preventDefault();
                const section = this.extractSectionFromOnclick(link.getAttribute('onclick'));
                if (section) {
                    this.showSection(section);
                }
            }
        });

        // Configurar busca com Enter
        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const target = e.target;
                
                // Busca em empresas
                if (target.id === 'searchCompanies') {
                    empresasManager.search();
                }
                
                // Busca em usuários
                if (target.id === 'searchUsers') {
                    usuariosManager.search();
                }
                
                // Busca em aplicações
                if (target.id === 'searchApplications') {
                    aplicacoesManager.search();
                }
                
                // Busca em aplicações de clientes
                if (target.id === 'searchClientApps') {
                    aplicacoesManager.searchClientApps();
                }
            }
        });

        // Tratar erros globais
        window.addEventListener('error', (e) => {
            console.error('Erro global capturado:', e.error);
            
            // Não mostrar alertas para erros de recursos (imagens, scripts, etc)
            if (e.target !== window) {
                return;
            }
            
            showAlert('Ocorreu um erro inesperado. Verifique o console para mais detalhes.', 'danger');
        });

        // Tratar promessas rejeitadas
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Promise rejeitada não tratada:', e.reason);
            
            // Não mostrar alert para erros de rede já tratados
            if (e.reason?.message?.includes('fetch')) {
                return;
            }
            
            showAlert('Erro na aplicação. Verifique sua conexão e tente novamente.', 'warning');
        });
    }

    extractSectionFromOnclick(onclickString) {
        const match = onclickString.match(/showSection\(['"]([^'"]+)['"]\)/);
        return match ? match[1] : null;
    }

    checkInitialAuth() {
        // O AuthManager já faz essa verificação, mas vamos garantir
        // que a interface esteja correta
        if (api.isAuthenticated()) {
            // Se estiver autenticado, garantir que está na tela correta
            setTimeout(() => {
                if (!document.getElementById('dashboardScreen').classList.contains('d-none')) {
                    this.showSection('dashboard');
                }
            }, 100);
        }
    }

    showSection(section) {
        // Verificar autenticação
        if (!api.isAuthenticated() && section !== 'login') {
            authManager.showLogin();
            return;
        }

        this.currentSection = section;
        
        // Atualizar menu ativo
        this.updateActiveMenu(section);
        
        // Carregar seção correspondente
        switch (section) {
            case 'dashboard':
                dashboard.loadDashboard();
                break;
                
            case 'empresas':
                empresasManager.loadEmpresas();
                break;
                
            case 'usuarios':
                usuariosManager.loadUsuarios();
                break;
                
            case 'aplicacoes':
                aplicacoesManager.loadAplicacoes();
                break;
                
            case 'aplicacoes-cliente':
                aplicacoesManager.loadAplicacoesCliente();
                break;
                
            default:
                console.warn('Seção não encontrada:', section);
                this.showSection('dashboard');
        }
    }

    updateActiveMenu(activeSection) {
        // Remover classe active de todos os itens
        document.querySelectorAll('.list-group-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Adicionar classe active ao item correspondente
        const sectionMap = {
            'dashboard': 'dashboard',
            'empresas': 'empresas',
            'usuarios': 'usuarios',
            'aplicacoes': 'aplicacoes',
            'aplicacoes-cliente': 'aplicacoes-cliente'
        };
        
        const menuSection = sectionMap[activeSection];
        if (menuSection) {
            const menuItem = document.querySelector(`[onclick*="showSection('${menuSection}')"]`);
            if (menuItem) {
                menuItem.classList.add('active');
            }
        }
    }

    // Métodos utilitários para toda a aplicação
    
    formatApiError(error) {
        if (error.response && error.response.data && error.response.data.detail) {
            return error.response.data.detail;
        }
        
        if (error.message) {
            return error.message;
        }
        
        return 'Erro desconhecido';
    }

    validateJsonField(value, fieldName) {
        if (!value || value.trim() === '') {
            return null;
        }
        
        try {
            return JSON.parse(value);
        } catch (error) {
            throw new Error(`JSON inválido no campo ${fieldName}: ${error.message}`);
        }
    }

    formatCurrency(value) {
        if (!value) return 'R$ 0,00';
        
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Método para refresh geral da aplicação
    async refreshCurrentSection() {
        showLoading(true);
        
        try {
            switch (this.currentSection) {
                case 'dashboard':
                    await dashboard.refreshMetrics();
                    break;
                    
                case 'empresas':
                    await empresasManager.loadCompaniesData();
                    break;
                    
                case 'usuarios':
                    await usuariosManager.loadUsersData();
                    break;
                    
                case 'aplicacoes':
                    await aplicacoesManager.loadApplicationsData();
                    break;
                    
                case 'aplicacoes-cliente':
                    await aplicacoesManager.loadClientApplicationsData();
                    break;
            }
            
            showAlert('Dados atualizados!', 'success', 2000);
            
        } catch (error) {
            showAlert('Erro ao atualizar dados: ' + this.formatApiError(error), 'danger');
        } finally {
            showLoading(false);
        }
    }

    // Método para logout global
    logout() {
        if (confirm('Tem certeza que deseja sair?')) {
            authManager.logout();
        }
    }

    // Método para verificar conexão com API
    async checkApiConnection() {
        try {
            await api.healthCheck();
            showAlert('Conexão com API: OK', 'success', 2000);
            return true;
        } catch (error) {
            showAlert('Falha na conexão com API', 'danger');
            return false;
        }
    }
}

// Funções globais para compatibilidade com o HTML
function showSection(section) {
    if (window.app) {
        window.app.showSection(section);
    }
}

function logout() {
    if (window.app) {
        window.app.logout();
    }
}

// Instância global da aplicação
window.app = new App();

// Exportar para uso em outros módulos se necessário
if (typeof module !== 'undefined' && module.exports) {
    module.exports = App;
}