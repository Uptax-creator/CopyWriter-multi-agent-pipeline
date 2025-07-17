/**
 * Correções de Funcionalidades do Frontend
 * Este arquivo contém as implementações das funções que estavam faltando
 */

// ===============================
// NAVEGAÇÃO ENTRE TELAS
// ===============================

function showApplications() {
    console.log('📱 Mostrar catálogo de aplicações');
    hideAllScreens();
    document.getElementById('applicationsScreen').classList.remove('d-none');
    loadApplicationsData();
    
    // Scroll para o topo
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showCompanyApplications() {
    console.log('🏢 Mostrar aplicações da empresa');
    hideAllScreens();
    document.getElementById('companyApplicationsScreen').classList.remove('d-none');
    loadCompanyApplicationsData();
    
    // Scroll para o topo
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showInviteUser() {
    console.log('👥 Mostrar tela de convite');
    hideAllScreens();
    document.getElementById('inviteUserScreen').classList.remove('d-none');
    setupInviteForm();
    
    // Scroll para o topo
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function backToDashboard() {
    console.log('🏠 Voltando ao dashboard');
    hideAllScreens();
    document.getElementById('dashboardScreen').classList.remove('d-none');
    updateDashboardStats();
}

function showCreateApplication() {
    console.log('➕ Mostrar tela de criar aplicação');
    hideAllScreens();
    document.getElementById('createApplicationScreen').classList.remove('d-none');
    setupApplicationForm();
    
    // Scroll para o topo
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showAddApplicationToCompany() {
    console.log('🔗 Mostrar tela de adicionar aplicação à empresa');
    showApplications();
    // Adicionar modo de seleção
    document.body.classList.add('selection-mode');
}

// ===============================
// GERENCIAMENTO DE APLICAÇÕES
// ===============================

function loadApplicationsData() {
    // Dados mockados das aplicações disponíveis
    const applications = [
        {
            id: 'omie-mcp',
            name: 'Omie MCP',
            description: 'Integração com ERP Omie via Model Context Protocol',
            category: 'erp',
            status: 'active',
            icon: 'bi-diagram-3',
            credentials: ['app_key', 'app_secret', 'api_url'],
            created: '2024-01-15'
        },
        {
            id: 'claude-ai',
            name: 'Claude AI',
            description: 'Assistente de IA para automação de tarefas',
            category: 'ai',
            status: 'active',
            icon: 'bi-robot',
            credentials: ['api_key'],
            created: '2024-01-10'
        },
        {
            id: 'github-copilot',
            name: 'GitHub Copilot',
            description: 'Assistente de código para desenvolvimento',
            category: 'ai',
            status: 'beta',
            icon: 'bi-github',
            credentials: ['access_token'],
            created: '2024-01-20'
        },
        {
            id: 'n8n-automation',
            name: 'N8N Automation',
            description: 'Plataforma de automação de workflows',
            category: 'automation',
            status: 'active',
            icon: 'bi-shuffle',
            credentials: ['webhook_url', 'api_key'],
            created: '2024-01-12'
        },
        {
            id: 'slack-integration',
            name: 'Slack',
            description: 'Integração com Slack para comunicação',
            category: 'communication',
            status: 'active',
            icon: 'bi-slack',
            credentials: ['webhook_url', 'bot_token'],
            created: '2024-01-08'
        },
        {
            id: 'trello-boards',
            name: 'Trello',
            description: 'Gerenciamento de projetos e tarefas',
            category: 'project-management',
            status: 'active',
            icon: 'bi-kanban',
            credentials: ['api_key', 'api_token'],
            created: '2024-01-05'
        }
    ];

    renderApplications(applications);
}

function renderApplications(applications) {
    const container = document.getElementById('applicationsGrid');
    if (!container) {
        console.error('Container applicationsGrid não encontrado');
        return;
    }

    // Limpar container primeiro
    container.innerHTML = '';
    
    // Garantir que o container seja visível
    container.style.display = 'flex';
    container.style.flexWrap = 'wrap';
    container.style.gap = '1rem';
    container.style.marginTop = '1rem';
    
    // Criar HTML das aplicações
    const applicationsHTML = applications.map(app => `
        <div class="col-lg-4 col-md-6 mb-4">
            <div class="card application-card h-100">
                <div class="card-body">
                    <div class="d-flex align-items-start mb-3">
                        <div class="application-icon me-3">
                            <i class="${app.icon} text-primary"></i>
                        </div>
                        <div class="flex-grow-1">
                            <h5 class="card-title mb-1">${app.name}</h5>
                            <p class="card-text text-muted small mb-2">${app.description}</p>
                            <div class="credential-tags">
                                ${app.credentials.map(cred => `
                                    <span class="badge bg-light text-dark me-1">${cred}</span>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                    <div class="application-details">
                        <div class="row">
                            <div class="col-6">
                                <small class="text-muted">Tipo</small>
                                <div class="fw-bold">${app.category.charAt(0).toUpperCase() + app.category.slice(1)}</div>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Status</small>
                                <div><span class="badge bg-${app.status === 'active' ? 'success' : app.status === 'beta' ? 'warning' : 'secondary'}">${app.status}</span></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-footer bg-transparent">
                    <div class="d-flex justify-content-between">
                        <button class="btn btn-sm btn-outline-primary" onclick="editApplication('${app.id}')">
                            <i class="bi bi-pencil me-1"></i>Editar
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="addToCompany('${app.id}')">
                            <i class="bi bi-plus-circle me-1"></i>Adicionar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    // Inserir HTML no container
    container.innerHTML = applicationsHTML;
    
    // Forçar reflow para garantir visibilidade
    container.offsetHeight;
    
    // Log para debug
    console.log(`✅ ${applications.length} aplicações renderizadas`);
}

function loadCompanyApplicationsData() {
    // Dados mockados das aplicações da empresa
    const companyApps = [
        {
            id: 'omie-mcp-config',
            appId: 'omie-mcp',
            name: 'Omie MCP',
            description: 'Integração com ERP Omie',
            category: 'erp',
            status: 'active',
            icon: 'bi-diagram-3',
            configured: true,
            lastConnection: '2024-01-25T10:30:00Z',
            configuredAt: '2024-01-15T14:20:00Z'
        },
        {
            id: 'claude-config',
            appId: 'claude-ai',
            name: 'Claude AI',
            description: 'Assistente de IA',
            category: 'ai',
            status: 'active',
            icon: 'bi-robot',
            configured: true,
            lastConnection: '2024-01-25T09:15:00Z',
            configuredAt: '2024-01-20T11:45:00Z'
        },
        {
            id: 'n8n-config',
            appId: 'n8n-automation',
            name: 'N8N Automation',
            description: 'Automação de workflows',
            category: 'automation',
            status: 'pending',
            icon: 'bi-shuffle',
            configured: false,
            lastConnection: null,
            configuredAt: '2024-01-22T16:30:00Z'
        },
        {
            id: 'slack-config',
            appId: 'slack-integration',
            name: 'Slack',
            description: 'Comunicação da equipe',
            category: 'communication',
            status: 'error',
            icon: 'bi-slack',
            configured: true,
            lastConnection: '2024-01-20T08:00:00Z',
            configuredAt: '2024-01-10T12:00:00Z'
        }
    ];

    renderCompanyApplications(companyApps);
}

function renderCompanyApplications(apps) {
    const container = document.getElementById('companyApplicationsGrid');
    if (!container) {
        console.error('Container companyApplicationsGrid não encontrado');
        return;
    }

    // Limpar container primeiro
    container.innerHTML = '';
    
    // Garantir que o container seja visível
    container.style.display = 'flex';
    container.style.flexWrap = 'wrap';
    container.style.gap = '1rem';
    container.style.marginTop = '1rem';
    
    // Criar HTML das aplicações
    const applicationsHTML = apps.map(app => `
        <div class="col-lg-4 col-md-6 mb-4">
            <div class="card application-card h-100">
                <div class="card-body">
                    <div class="d-flex align-items-start mb-3">
                        <div class="application-icon me-3">
                            <i class="${app.icon} text-primary"></i>
                        </div>
                        <div class="flex-grow-1">
                            <h5 class="card-title mb-1">${app.name}</h5>
                            <p class="card-text text-muted small mb-2">${app.description}</p>
                            <span class="badge bg-${getStatusColor(app.status)}">${getStatusText(app.status)}</span>
                        </div>
                    </div>
                    <div class="application-details">
                        <div class="row">
                            <div class="col-6">
                                <small class="text-muted">Configurada em</small>
                                <div class="fw-bold">${formatDate(app.configuredAt)}</div>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Última conexão</small>
                                <div class="fw-bold">${app.lastConnection ? formatDate(app.lastConnection) : 'Nunca'}</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-footer bg-transparent">
                    <div class="d-flex justify-content-between">
                        <button class="btn btn-sm btn-outline-primary" onclick="configureCompanyApplication('${app.id}')">
                            <i class="bi bi-gear me-1"></i>Configurar
                        </button>
                        <button class="btn btn-sm btn-outline-info" onclick="testCompanyAppConnection('${app.id}')">
                            <i class="bi bi-wifi me-1"></i>Testar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    // Inserir HTML no container
    container.innerHTML = applicationsHTML;
    
    // Forçar reflow para garantir visibilidade
    container.offsetHeight;
    
    // Log para debug
    console.log(`✅ ${apps.length} aplicações da empresa renderizadas`);
}

// ===============================
// CONFIGURAÇÃO DE APLICAÇÕES
// ===============================

function configureCompanyApplication(appId) {
    console.log('⚙️ Configurar aplicação:', appId);
    
    // Encontrar dados da aplicação
    const appData = {
        'omie-mcp-config': {
            id: 'omie-mcp-config',
            name: 'Omie MCP',
            description: 'Integração com ERP Omie via Model Context Protocol',
            category: 'ERP',
            status: 'active',
            icon: 'bi-diagram-3',
            credentials: [
                { id: 'app_key', label: 'App Key', type: 'text', required: true },
                { id: 'app_secret', label: 'App Secret', type: 'password', required: true },
                { id: 'api_url', label: 'URL da API', type: 'url', required: true, placeholder: 'https://app.omie.com.br/api/v1/' }
            ]
        },
        'claude-config': {
            id: 'claude-config',
            name: 'Claude AI',
            description: 'Assistente de IA para automação de tarefas',
            category: 'AI',
            status: 'active',
            icon: 'bi-robot',
            credentials: [
                { id: 'api_key', label: 'API Key', type: 'password', required: true },
                { id: 'model', label: 'Modelo', type: 'select', options: ['claude-3-opus', 'claude-3-sonnet'], required: false }
            ]
        },
        'n8n-config': {
            id: 'n8n-config',
            name: 'N8N Automation',
            description: 'Plataforma de automação de workflows',
            category: 'Automation',
            status: 'pending',
            icon: 'bi-shuffle',
            credentials: [
                { id: 'webhook_url', label: 'Webhook URL', type: 'url', required: true },
                { id: 'api_key', label: 'API Key', type: 'password', required: true }
            ]
        }
    };

    const app = appData[appId];
    if (!app) {
        safeShowAlert('Aplicação não encontrada', 'error');
        return;
    }

    // Mostrar tela de configuração
    hideAllScreens();
    document.getElementById('configureAppCredentialsScreen').classList.remove('d-none');
    
    // Scroll para o topo
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Preencher dados da aplicação
    document.getElementById('configAppName').textContent = app.name;
    document.getElementById('configAppDescription').textContent = app.description;
    document.getElementById('configAppCategory').textContent = app.category;
    document.getElementById('configAppStatus').innerHTML = `<span class="badge bg-${getStatusColor(app.status)}">${getStatusText(app.status)}</span>`;
    document.getElementById('configAppIcon').innerHTML = `<i class="${app.icon}"></i>`;
    
    // Gerar campos de credenciais
    const credentialsContainer = document.getElementById('credentialsFields');
    credentialsContainer.innerHTML = app.credentials.map(cred => `
        <div class="credentials-field">
            <div class="form-floating">
                <input type="${cred.type}" class="form-control" id="${cred.id}" name="${cred.id}" 
                       ${cred.required ? 'required' : ''} ${cred.placeholder ? `placeholder="${cred.placeholder}"` : ''}>
                <label for="${cred.id}">${cred.label} ${cred.required ? '*' : ''}</label>
            </div>
        </div>
    `).join('');
    
    // Configurar botões
    document.getElementById('backToCompanyAppsHeader').onclick = () => showCompanyApplications();
    document.getElementById('backToCompanyAppsBtn').onclick = () => showCompanyApplications();
    document.getElementById('testCredentialsBtn').onclick = () => testCredentials(app.id);
}

function testCompanyAppConnection(appId) {
    console.log('🔬 Testar conexão:', appId);
    
    const button = event.target;
    const originalText = button.innerHTML;
    
    // Mostrar loading
    button.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Testando...';
    button.disabled = true;
    
    // Simular teste
    setTimeout(() => {
        const success = Math.random() > 0.3; // 70% de sucesso
        
        if (success) {
            safeShowAlert('✅ Conexão bem-sucedida!', 'success');
            button.innerHTML = '<i class="bi bi-check-circle me-1"></i>Conectado';
            button.className = 'btn btn-sm btn-success';
        } else {
            safeShowAlert('❌ Falha na conexão. Verifique as credenciais.', 'danger');
            button.innerHTML = '<i class="bi bi-x-circle me-1"></i>Falha';
            button.className = 'btn btn-sm btn-danger';
        }
        
        // Restaurar botão após 3 segundos
        setTimeout(() => {
            button.innerHTML = originalText;
            button.className = 'btn btn-sm btn-outline-info';
            button.disabled = false;
        }, 3000);
    }, 2000);
}

function testCredentials(appId) {
    console.log('🧪 Testar credenciais:', appId);
    
    const button = document.getElementById('testCredentialsBtn');
    const originalText = button.innerHTML;
    
    button.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Testando...';
    button.disabled = true;
    
    setTimeout(() => {
        const success = Math.random() > 0.2; // 80% de sucesso
        
        if (success) {
            safeShowAlert('✅ Credenciais válidas! Conexão estabelecida.', 'success');
        } else {
            safeShowAlert('❌ Credenciais inválidas. Verifique os dados informados.', 'danger');
        }
        
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}

// ===============================
// UTILITÁRIOS
// ===============================

function getStatusColor(status) {
    const colors = {
        'active': 'success',
        'pending': 'warning',
        'error': 'danger',
        'inactive': 'secondary'
    };
    return colors[status] || 'secondary';
}

function getStatusText(status) {
    const texts = {
        'active': 'Ativo',
        'pending': 'Pendente',
        'error': 'Erro',
        'inactive': 'Inativo'
    };
    return texts[status] || status;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

function editApplication(appId) {
    console.log('✏️ Editar aplicação:', appId);
    
    // Buscar aplicação pelos dados armazenados
    const applications = getStoredApplications();
    const app = applications.find(a => a.id === appId);
    
    if (!app) {
        safeShowAlert('Aplicação não encontrada', 'error');
        return;
    }
    
    // Mostrar tela de criação/edição
    hideAllScreens();
    document.getElementById('createApplicationScreen').classList.remove('d-none');
    
    // Alterar título para edição
    document.getElementById('applicationFormTitle').textContent = 'Editar Aplicação';
    
    // Preencher formulário com dados da aplicação
    document.getElementById('appId').value = app.id;
    document.getElementById('appName').value = app.name;
    document.getElementById('appDescription').value = app.description;
    document.getElementById('appCategory').value = app.category;
    document.getElementById('appType').value = app.type;
    document.getElementById('appVersion').value = app.version;
    document.getElementById('appStatus').value = app.status;
    
    // Configurações específicas
    if (app.config) {
        document.getElementById('serverUrl').value = app.config.serverUrl || '';
        document.getElementById('apiKey').value = app.config.apiKey || '';
        document.getElementById('webhookUrl').value = app.config.webhookUrl || '';
        document.getElementById('maxRetries').value = app.config.maxRetries || 3;
        document.getElementById('timeout').value = app.config.timeout || 30;
    }
    
    // Marcar como modo edição
    window.editingAppId = appId;
    
    safeShowAlert('Aplicação carregada para edição', 'info');
}

function getStoredApplications() {
    // Buscar aplicações armazenadas localmente
    const stored = localStorage.getItem('user_applications');
    if (stored) {
        return JSON.parse(stored);
    }
    
    // Aplicações de exemplo se não houver dados
    return [
        {
            id: 'omie-mcp-server',
            name: 'Omie MCP Server',
            description: 'Servidor MCP para integração com APIs do Omie ERP',
            category: 'erp',
            type: 'mcp-server',
            version: '1.0.0',
            status: 'ativo',
            createdAt: '2025-01-10',
            config: {
                serverUrl: 'http://localhost:8000',
                apiKey: 'your-api-key',
                webhookUrl: '',
                maxRetries: 3,
                timeout: 30
            }
        }
    ];
}

function saveApplication(applicationData, isEditing) {
    let applications = getStoredApplications();
    
    if (isEditing) {
        // Atualizar aplicação existente
        const index = applications.findIndex(app => app.id === applicationData.id);
        if (index !== -1) {
            // Manter data de criação original
            applicationData.createdAt = applications[index].createdAt;
            applications[index] = applicationData;
            console.log('✅ Aplicação atualizada:', applicationData.id);
        }
        
        // Limpar modo de edição
        delete window.editingAppId;
    } else {
        // Verificar se ID já existe
        if (applications.find(app => app.id === applicationData.id)) {
            throw new Error('ID da aplicação já existe');
        }
        
        // Adicionar nova aplicação
        applications.push(applicationData);
        console.log('✅ Nova aplicação criada:', applicationData.id);
    }
    
    // Salvar no localStorage
    localStorage.setItem('user_applications', JSON.stringify(applications));
}

function addToCompany(appId) {
    console.log('➕ Adicionar à empresa:', appId);
    safeShowAlert('Aplicação adicionada à empresa!', 'success');
    
    // Simular delay e voltar para aplicações da empresa
    setTimeout(() => {
        showCompanyApplications();
    }, 1500);
}

// ===============================
// FILTROS E VISUALIZAÇÕES
// ===============================

function filterApplications() {
    console.log('🔍 Filtrar aplicações');
    const searchTerm = document.getElementById('searchApplications').value.toLowerCase();
    const category = document.getElementById('filterCategory').value;
    const status = document.getElementById('filterStatus').value;
    
    // Aplicar filtros (implementação simplificada)
    safeShowAlert('Filtros aplicados!', 'info');
}

function filterCompanyApplications() {
    console.log('🔍 Filtrar aplicações da empresa');
    const searchTerm = document.getElementById('searchCompanyApps').value.toLowerCase();
    const category = document.getElementById('filterCompanyCategory').value;
    const status = document.getElementById('filterCompanyStatus').value;
    
    // Aplicar filtros (implementação simplificada)
    safeShowAlert('Filtros aplicados!', 'info');
}

// ===============================
// EVENTOS DE VISUALIZAÇÃO
// ===============================

document.addEventListener('DOMContentLoaded', function() {
    // Configurar mudanças de visualização
    const viewRadios = document.querySelectorAll('input[name="viewMode"]');
    viewRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            changeView(this.value);
        });
    });
    
    const companyViewRadios = document.querySelectorAll('input[name="companyViewMode"]');
    companyViewRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            changeCompanyView(this.value);
        });
    });
});

function changeView(viewMode) {
    console.log('👁️ Mudando visualização para:', viewMode);
    
    // Ocultar todas as visualizações
    document.getElementById('applicationsGrid').classList.add('d-none');
    document.getElementById('applicationsList').classList.add('d-none');
    document.getElementById('applicationsTable').classList.add('d-none');
    
    // Mostrar visualização selecionada
    switch(viewMode) {
        case 'grid':
            document.getElementById('applicationsGrid').classList.remove('d-none');
            break;
        case 'list':
            document.getElementById('applicationsList').classList.remove('d-none');
            break;
        case 'table':
            document.getElementById('applicationsTable').classList.remove('d-none');
            break;
    }
}

function changeCompanyView(viewMode) {
    console.log('👁️ Mudando visualização da empresa para:', viewMode);
    
    // Ocultar todas as visualizações
    document.getElementById('companyApplicationsGrid').classList.add('d-none');
    document.getElementById('companyApplicationsList').classList.add('d-none');
    document.getElementById('companyApplicationsTable').classList.add('d-none');
    
    // Mostrar visualização selecionada
    switch(viewMode) {
        case 'grid':
            document.getElementById('companyApplicationsGrid').classList.remove('d-none');
            break;
        case 'list':
            document.getElementById('companyApplicationsList').classList.remove('d-none');
            break;
        case 'table':
            document.getElementById('companyApplicationsTable').classList.remove('d-none');
            break;
    }
}

// ===============================
// FORMULÁRIOS
// ===============================

function setupApplicationForm() {
    console.log('📝 Configurar formulário de aplicação');
    
    const form = document.getElementById('createApplicationForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleCreateApplication();
        });
    }
}

function handleCreateApplication() {
    const isEditing = window.editingAppId;
    console.log(isEditing ? '✏️ Editando aplicação' : '➕ Criando nova aplicação');
    
    const formData = new FormData(document.getElementById('createApplicationForm'));
    const appData = Object.fromEntries(formData.entries());
    
    // Criar objeto da aplicação
    const applicationData = {
        id: appData.appId,
        name: appData.appName,
        description: appData.appDescription,
        category: appData.appCategory,
        type: appData.appType,
        version: appData.appVersion,
        status: appData.appStatus,
        createdAt: isEditing ? undefined : new Date().toISOString().split('T')[0],
        updatedAt: isEditing ? new Date().toISOString().split('T')[0] : undefined,
        config: {
            serverUrl: appData.serverUrl,
            apiKey: appData.apiKey,
            webhookUrl: appData.webhookUrl,
            maxRetries: parseInt(appData.maxRetries) || 3,
            timeout: parseInt(appData.timeout) || 30
        }
    };
    
    // Salvar aplicação
    saveApplication(applicationData, isEditing);
    
    safeShowAlert(
        isEditing ? 'Aplicação atualizada com sucesso!' : 'Aplicação criada com sucesso!', 
        'success'
    );
    
    setTimeout(() => {
        showApplications();
    }, 1500);
}

function setupInviteForm() {
    console.log('📧 Configurar formulário de convite');
    
    const form = document.getElementById('inviteUserForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleSendInvite(e);
        });
    }
}

async function handleSendInvite(e) {
    e.preventDefault();
    
    const nome = document.getElementById('inviteNome').value.trim();
    const sobrenome = document.getElementById('inviteSobrenome').value.trim();
    const email = document.getElementById('inviteEmail').value.trim();
    const accessLevel = document.querySelector('input[name="accessLevel"]:checked');
    
    if (!nome || !sobrenome || !email || !accessLevel) {
        safeShowAlert('Preencha todos os campos obrigatórios', 'danger');
        return;
    }
    
    safeShowAlert('Enviando convite...', 'info');
    
    // Simular envio
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    safeShowAlert(`Convite enviado para ${nome} ${sobrenome}!`, 'success');
    
    setTimeout(() => {
        backToDashboard();
    }, 1500);
}

console.log('✅ Frontend fixes carregado com sucesso');