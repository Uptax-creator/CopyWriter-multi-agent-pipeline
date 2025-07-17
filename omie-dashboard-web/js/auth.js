/**
 * Módulo de Autenticação
 */

class AuthManager {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        // Verificar se já está logado
        if (api.isAuthenticated()) {
            this.showDashboard();
        } else {
            this.showLogin();
        }
        
        // Configurar eventos
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Form de login
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        // Form de criar aplicação
        const createAppForm = document.getElementById('createAppForm');
        if (createAppForm) {
            createAppForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleCreateApp();
            });
        }
    }

    async handleLogin() {
        const appKey = document.getElementById('appKey').value.trim();
        const appSecret = document.getElementById('appSecret').value.trim();
        const errorDiv = document.getElementById('loginError');

        // Limpar erros anteriores
        errorDiv.classList.add('d-none');

        if (!appKey || !appSecret) {
            this.showLoginError('Por favor, preencha todos os campos');
            return;
        }

        try {
            // Fazer login na API
            const response = await api.login(appKey, appSecret);
            
            // Sucesso
            this.currentUser = {
                app_key: appKey,
                expires_at: response.expires_in
            };
            
            showAlert('Login realizado com sucesso!', 'success', 2000);
            this.showDashboard();
            
        } catch (error) {
            this.showLoginError('Credenciais inválidas. Verifique APP_KEY e APP_SECRET.');
        }
    }

    showLoginError(message) {
        const errorDiv = document.getElementById('loginError');
        errorDiv.textContent = message;
        errorDiv.classList.remove('d-none');
    }

    showLogin() {
        document.getElementById('loginScreen').classList.remove('d-none');
        document.getElementById('dashboardScreen').classList.add('d-none');
        
        // Limpar formulário
        const form = document.getElementById('loginForm');
        if (form) {
            form.reset();
        }
        
        // Limpar erros
        const errorDiv = document.getElementById('loginError');
        if (errorDiv) {
            errorDiv.classList.add('d-none');
        }
    }

    showDashboard() {
        document.getElementById('loginScreen').classList.add('d-none');
        document.getElementById('dashboardScreen').classList.remove('d-none');
        
        // Atualizar info do usuário
        const userInfo = document.getElementById('userInfo');
        if (userInfo && this.currentUser) {
            userInfo.textContent = this.currentUser.app_key;
        }
        
        // Carregar dashboard inicial
        showSection('dashboard');
    }

    logout() {
        api.logout();
        this.currentUser = null;
        this.showLogin();
        showAlert('Logout realizado com sucesso!', 'info', 2000);
    }

    // Criar nova aplicação (para usuários sem credenciais)
    async handleCreateApp() {
        const description = document.getElementById('appDescription').value.trim();
        const type = document.getElementById('appType').value;

        if (!description || !type) {
            showAlert('Por favor, preencha todos os campos', 'warning');
            return;
        }

        try {
            // Criar aplicação sem autenticação
            const response = await fetch('http://127.0.0.1:8003/aplicacoes/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    descricao: description,
                    tipo: type
                })
            });

            if (!response.ok) {
                throw new Error(`Erro ${response.status}`);
            }

            const data = await response.json();

            // Mostrar credenciais geradas
            this.showGeneratedCredentials(data);

        } catch (error) {
            showAlert('Erro ao criar aplicação: ' + error.message, 'danger');
        }
    }

    showGeneratedCredentials(data) {
        // Fechar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('createAppModal'));
        modal.hide();

        // Mostrar modal com credenciais
        const credentialsHtml = `
            <div class="modal fade" id="credentialsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-success text-white">
                            <h5 class="modal-title">
                                <i class="bi bi-check-circle me-2"></i>Aplicação Criada com Sucesso!
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-warning">
                                <i class="bi bi-exclamation-triangle me-2"></i>
                                <strong>IMPORTANTE:</strong> Guarde estas credenciais em local seguro. 
                                O APP_SECRET não será exibido novamente!
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <label class="form-label fw-bold">APP_KEY:</label>
                                    <div class="input-group">
                                        <input type="text" class="form-control credential-display" value="${data.app_key}" readonly>
                                        <button class="btn btn-outline-primary" onclick="copyToClipboard('${data.app_key}')">
                                            <i class="bi bi-clipboard"></i>
                                        </button>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-bold">APP_SECRET:</label>
                                    <div class="input-group">
                                        <input type="text" class="form-control credential-display" value="${data.app_secret}" readonly>
                                        <button class="btn btn-outline-primary" onclick="copyToClipboard('${data.app_secret}')">
                                            <i class="bi bi-clipboard"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                            
                            <hr>
                            
                            <h6>Detalhes da Aplicação:</h6>
                            <ul class="list-unstyled">
                                <li><strong>Descrição:</strong> ${data.descricao}</li>
                                <li><strong>Tipo:</strong> ${data.tipo}</li>
                                <li><strong>ID:</strong> ${data.id_aplicacao}</li>
                            </ul>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-success" onclick="useGeneratedCredentials('${data.app_key}', '${data.app_secret}')">
                                <i class="bi bi-box-arrow-in-right me-2"></i>Usar estas credenciais para entrar
                            </button>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Adicionar modal ao DOM
        document.body.insertAdjacentHTML('beforeend', credentialsHtml);
        
        // Mostrar modal
        const credentialsModal = new bootstrap.Modal(document.getElementById('credentialsModal'));
        credentialsModal.show();

        // Limpar modal quando fechar
        document.getElementById('credentialsModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }
}

// Função global para usar credenciais geradas
function useGeneratedCredentials(appKey, appSecret) {
    // Preencher formulário de login
    document.getElementById('appKey').value = appKey;
    document.getElementById('appSecret').value = appSecret;
    
    // Fechar modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('credentialsModal'));
    modal.hide();
    
    // Focar no botão de login
    document.querySelector('#loginForm button[type="submit"]').focus();
    
    showAlert('Credenciais preenchidas! Clique em "Entrar" para fazer login.', 'info', 3000);
}

// Função global para mostrar modal de criar aplicação
function showCreateApp() {
    const modal = new bootstrap.Modal(document.getElementById('createAppModal'));
    modal.show();
}

// Função global para logout
function logout() {
    authManager.logout();
}

// Função global para criar aplicação
function createApplication() {
    authManager.handleCreateApp();
}

// Inicializar gerenciador de autenticação
let authManager;

document.addEventListener('DOMContentLoaded', () => {
    authManager = new AuthManager();
});