/**
 * Aplicação Principal v2.0
 * Controlador principal do novo frontend
 */

class App {
    constructor() {
        this.version = '2.0';
        this.initialized = false;
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
        if (this.initialized) return;
        
        console.log(`Omie Tenant Manager v${this.version} - Frontend iniciado`);
        
        // Configurar eventos globais
        this.setupGlobalEvents();
        
        // Marcar como inicializado
        this.initialized = true;
        
        // Log de debug
        this.logSystemInfo();
    }

    setupGlobalEvents() {
        // Capturar apenas erros críticos
        window.addEventListener('error', (e) => {
            console.error('Erro global capturado:', e.error);
            
            // Não mostrar alertas para erros de recursos ou scripts externos
            if (e.target !== window || e.filename?.includes('cdn.jsdelivr.net')) {
                return;
            }
            
            // Filtrar erros conhecidos/menores
            const ignoredErrors = [
                'Script error',
                'ResizeObserver loop limit exceeded',
                'Non-Error promise rejection',
                'SecurityError'
            ];
            
            if (ignoredErrors.some(ignored => e.message?.includes(ignored))) {
                return;
            }
            
            // Só mostrar alerta para erros realmente críticos
            console.warn('Erro crítico detectado, mas não exibindo alerta para melhor UX');
        });

        // Capturar promessas rejeitadas críticas
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Promise rejeitada:', e.reason);
            
            // Não mostrar alert para erros já tratados ou conhecidos
            if (e.reason?.message?.includes('fetch') || 
                e.reason?.message?.includes('network') ||
                e.reason?.message?.includes('Failed to fetch')) {
                return;
            }
            
            // Só logar, não mostrar alerta
            console.warn('Promise rejeitada, mas não exibindo alerta para melhor UX');
        });

        // Atalhos de teclado
        document.addEventListener('keydown', (e) => {
            // ESC para voltar/cancelar
            if (e.key === 'Escape') {
                this.handleEscapeKey();
            }
            
            // Ctrl/Cmd + K para search (futuro)
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                // TODO: Abrir search global
                console.log('Search shortcut pressed');
            }
        });

        // Otimização para mobile
        this.setupMobileOptimizations();
        
        // Detectar modo escuro do sistema
        this.setupDarkModeDetection();
    }

    handleEscapeKey() {
        // Se tem modal aberto, fechar
        const modals = document.querySelectorAll('.modal.show');
        if (modals.length > 0) {
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            });
            return;
        }

        // Se está em uma tela secundária, voltar
        const currentScreen = this.getCurrentScreen();
        switch (currentScreen) {
            case 'registerScreen':
            case 'loginScreen':
                authManager.showWelcome();
                break;
            case 'companySelectionScreen':
                // Não permitir voltar (usuário já logado)
                break;
            case 'dashboardScreen':
                // Não há lugar para voltar
                break;
        }
    }

    getCurrentScreen() {
        const screens = [
            'welcomeScreen',
            'registerScreen',
            'loginScreen', 
            'companySelectionScreen',
            'dashboardScreen'
        ];
        
        return screens.find(screenId => {
            const screen = document.getElementById(screenId);
            return screen && !screen.classList.contains('d-none');
        });
    }

    setupMobileOptimizations() {
        // Prevenir zoom em inputs no iOS
        if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
            const inputs = document.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('focus', () => {
                    if (input.style.fontSize < '16px') {
                        input.style.fontSize = '16px';
                    }
                });
            });
        }

        // Detectar orientação
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                // Reajustar interface se necessário
                this.handleOrientationChange();
            }, 100);
        });
    }

    handleOrientationChange() {
        // Fechar menu mobile se estiver aberto
        const navbarCollapse = document.querySelector('.navbar-collapse.show');
        if (navbarCollapse) {
            const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
            if (bsCollapse) bsCollapse.hide();
        }
    }

    setupDarkModeDetection() {
        // Detectar preferência do sistema
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        
        // TODO: Implementar modo escuro quando necessário
        prefersDark.addEventListener('change', (e) => {
            if (e.matches) {
                console.log('Sistema mudou para modo escuro');
            } else {
                console.log('Sistema mudou para modo claro');
            }
        });
    }

    // Métodos utilitários

    showAlert(message, type = 'info', duration = 5000) {
        // Implementação similar ao authManager.showAlert
        const existingAlerts = document.querySelectorAll('.alert-floating');
        existingAlerts.forEach(alert => alert.remove());
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show alert-floating`;
        alertDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            min-width: 300px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 12px;
        `;
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        if (duration > 0) {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, duration);
        }
    }

    formatError(error) {
        if (error.response?.data?.detail) {
            return error.response.data.detail;
        }
        
        if (error.message) {
            return error.message;
        }
        
        return 'Erro desconhecido';
    }

    validateEmail(email) {
        const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return pattern.test(email);
    }

    formatPhone(phone) {
        // Remover tudo que não é número
        const cleaned = phone.replace(/\D/g, '');
        
        // Formatar (11) 99999-9999
        if (cleaned.length === 11) {
            return `(${cleaned.slice(0,2)}) ${cleaned.slice(2,7)}-${cleaned.slice(7)}`;
        }
        
        // Formatar (11) 9999-9999
        if (cleaned.length === 10) {
            return `(${cleaned.slice(0,2)}) ${cleaned.slice(2,6)}-${cleaned.slice(6)}`;
        }
        
        return phone;
    }

    formatCNPJ(cnpj) {
        const cleaned = cnpj.replace(/\D/g, '');
        if (cleaned.length === 14) {
            return `${cleaned.slice(0,2)}.${cleaned.slice(2,5)}.${cleaned.slice(5,8)}/${cleaned.slice(8,12)}-${cleaned.slice(12)}`;
        }
        return cnpj;
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

    // Debug e logging

    logSystemInfo() {
        console.log('=== Omie Tenant Manager v2.0 ===');
        console.log('User Agent:', navigator.userAgent);
        console.log('Screen:', `${screen.width}x${screen.height}`);
        console.log('Viewport:', `${window.innerWidth}x${window.innerHeight}`);
        console.log('Local Storage:', localStorage.length, 'items');
        console.log('==================================');
    }

    // Métodos para futura integração com backend

    async healthCheck() {
        try {
            // TODO: Implementar quando backend estiver pronto
            console.log('Health check - Backend não implementado ainda');
            return { status: 'pending', message: 'Backend em desenvolvimento' };
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'error', message: error.message };
        }
    }

    getApiBaseUrl() {
        // Para desenvolvimento
        return window.location.hostname === 'localhost' 
            ? 'http://localhost:8003' 
            : 'https://api.omie-tenant-manager.com';
    }

    // Método para testes

    runTests() {
        console.log('Executando testes básicos...');
        
        // Teste de validação de email
        console.assert(this.validateEmail('test@example.com'), 'Email validation failed');
        console.assert(!this.validateEmail('invalid-email'), 'Email validation failed');
        
        // Teste de formatação
        console.assert(this.formatPhone('11999999999') === '(11) 99999-9999', 'Phone formatting failed');
        console.assert(this.formatCNPJ('12345678000190') === '12.345.678/0001-90', 'CNPJ formatting failed');
        
        console.log('Testes básicos concluídos ✓');
    }
}

// Inicializar aplicação
const app = new App();

// Disponibilizar globalmente para debug
window.app = app;

// Executar testes em desenvolvimento
if (window.location.hostname === 'localhost') {
    setTimeout(() => app.runTests(), 2000);
}