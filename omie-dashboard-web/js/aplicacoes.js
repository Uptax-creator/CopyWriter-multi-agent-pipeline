/**
 * Módulo de Gestão de Aplicações do Sistema e de Clientes
 */

class AplicacoesManager {
    constructor() {
        this.currentApplication = null;
        this.currentClientApp = null;
        this.filters = {
            search: '',
            tipo: null
        };
        this.clientAppFilters = {
            search: '',
            id_empresa: null,
            id_aplicacao: null
        };
        this.companies = [];
        this.applications = [];
    }

    async loadAplicacoes() {
        const content = document.getElementById('content');
        
        content.innerHTML = `
            <div class="fade-in">
                <!-- Header -->
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h2><i class="bi bi-app me-2"></i>Aplicações do Sistema</h2>
                        <p class="text-muted mb-0">Gestão de aplicações (Claude, Copilot, N8N, etc.)</p>
                    </div>
                    <div>
                        <button class="btn btn-primary" onclick="aplicacoesManager.showCreateModal()">
                            <i class="bi bi-plus-circle me-2"></i>Nova Aplicação
                        </button>
                    </div>
                </div>

                <!-- Filtros -->
                <div class="card mb-4">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="input-group">
                                    <input type="text" class="form-control" id="searchApplications" 
                                           placeholder="Buscar por descrição...">
                                    <button class="btn btn-outline-primary" onclick="aplicacoesManager.search()">
                                        <i class="bi bi-search"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <select class="form-select" id="filterAppType" onchange="aplicacoesManager.filterByType()">
                                    <option value="">Todos os tipos</option>
                                    <option value="claude">Claude Desktop</option>
                                    <option value="copilot">Microsoft Copilot Studio</option>
                                    <option value="n8n">N8N Workflow</option>
                                    <option value="api">API Personalizada</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <button class="btn btn-outline-secondary w-100" onclick="aplicacoesManager.clearFilters()">
                                    <i class="bi bi-x-circle me-1"></i>Limpar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Lista de Aplicações -->
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="bi bi-list me-2"></i>Aplicações Cadastradas</h6>
                    </div>
                    <div class="card-body">
                        <div id="applicationsList">
                            <div class="text-center">
                                <div class="spinner-border"></div>
                                <p class="mt-2">Carregando aplicações...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal Criar/Editar Aplicação -->
            <div class="modal fade" id="applicationModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="applicationModalTitle">Nova Aplicação</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="applicationForm">
                                <div class="mb-3">
                                    <label for="appDescription" class="form-label">Descrição *</label>
                                    <input type="text" class="form-control" id="appDescription" required>
                                    <div class="form-text">Nome ou descrição da aplicação</div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="appType" class="form-label">Tipo *</label>
                                    <select class="form-select" id="appType" required>
                                        <option value="">Selecione...</option>
                                        <option value="claude">Claude Desktop</option>
                                        <option value="copilot">Microsoft Copilot Studio</option>
                                        <option value="n8n">N8N Workflow</option>
                                        <option value="api">API Personalizada</option>
                                    </select>
                                </div>

                                <div class="mb-3">
                                    <label for="appStatus" class="form-label">Status</label>
                                    <select class="form-select" id="appStatus">
                                        <option value="true">Ativo</option>
                                        <option value="false">Inativo</option>
                                    </select>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="aplicacoesManager.saveApplication()">
                                <i class="bi bi-check-circle me-1"></i>Salvar
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal para Exibir Credenciais -->
            <div class="modal fade" id="credentialsViewModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Credenciais da Aplicação</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="credentialsContent">
                            <!-- Conteúdo será inserido dinamicamente -->
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Carregar dados
        await this.loadApplicationsData();
    }

    async loadAplicacoesCliente() {
        const content = document.getElementById('content');
        
        content.innerHTML = `
            <div class="fade-in">
                <!-- Header -->
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h2><i class="bi bi-link-45deg me-2"></i>Aplicações dos Clientes</h2>
                        <p class="text-muted mb-0">Aplicações vinculadas às empresas</p>
                    </div>
                    <div>
                        <button class="btn btn-primary" onclick="aplicacoesManager.showCreateClientAppModal()">
                            <i class="bi bi-link me-2"></i>Vincular Aplicação
                        </button>
                    </div>
                </div>

                <!-- Filtros -->
                <div class="card mb-4">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="input-group">
                                    <input type="text" class="form-control" id="searchClientApps" 
                                           placeholder="Buscar por nome...">
                                    <button class="btn btn-outline-primary" onclick="aplicacoesManager.searchClientApps()">
                                        <i class="bi bi-search"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <select class="form-select" id="filterClientCompany" onchange="aplicacoesManager.filterClientAppsByCompany()">
                                    <option value="">Todas as empresas</option>
                                </select>
                            </div>
                            <div class="col-md-2">
                                <select class="form-select" id="filterClientApplication" onchange="aplicacoesManager.filterClientAppsByApplication()">
                                    <option value="">Todas as aplicações</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <button class="btn btn-outline-secondary w-100" onclick="aplicacoesManager.clearClientAppFilters()">
                                    <i class="bi bi-x-circle me-1"></i>Limpar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Lista de Aplicações dos Clientes -->
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="bi bi-list me-2"></i>Aplicações Vinculadas</h6>
                    </div>
                    <div class="card-body">
                        <div id="clientApplicationsList">
                            <div class="text-center">
                                <div class="spinner-border"></div>
                                <p class="mt-2">Carregando aplicações dos clientes...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal Criar/Editar Aplicação do Cliente -->
            <div class="modal fade" id="clientAppModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="clientAppModalTitle">Vincular Aplicação</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="clientAppForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="clientAppName" class="form-label">Nome da Aplicação *</label>
                                            <input type="text" class="form-control" id="clientAppName" required>
                                            <div class="form-text">Nome personalizado para esta instância</div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="clientAppCompany" class="form-label">Empresa *</label>
                                            <select class="form-select" id="clientAppCompany" required>
                                                <option value="">Selecione uma empresa...</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                <div class="mb-3">
                                    <label for="clientAppApplication" class="form-label">Aplicação do Sistema *</label>
                                    <select class="form-select" id="clientAppApplication" required>
                                        <option value="">Selecione uma aplicação...</option>
                                    </select>
                                </div>

                                <div class="mb-3">
                                    <label for="clientAppOmieConfig" class="form-label">Configuração Omie (JSON)</label>
                                    <textarea class="form-control" id="clientAppOmieConfig" rows="4" 
                                              placeholder='{"app_key": "sua_app_key", "app_secret": "seu_app_secret"}'></textarea>
                                    <div class="form-text">Credenciais e configurações específicas do Omie</div>
                                </div>

                                <div class="mb-3">
                                    <label for="clientAppConfig" class="form-label">Configuração da Aplicação (JSON)</label>
                                    <textarea class="form-control" id="clientAppConfig" rows="4" 
                                              placeholder='{"webhook_url": "https://...", "custom_settings": {...}}'></textarea>
                                    <div class="form-text">Configurações específicas da aplicação</div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="aplicacoesManager.saveClientApplication()">
                                <i class="bi bi-check-circle me-1"></i>Salvar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Carregar dados
        await this.loadClientApplicationsData();
    }

    async loadApplicationsData() {
        try {
            this.applications = await api.getApplications();
            this.renderApplicationsList(this.applications.filter(app => {
                const matchesSearch = !this.filters.search || 
                    app.descricao.toLowerCase().includes(this.filters.search.toLowerCase());
                const matchesType = !this.filters.tipo || app.tipo === this.filters.tipo;
                return matchesSearch && matchesType;
            }));
        } catch (error) {
            document.getElementById('applicationsList').innerHTML = `
                <div class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    <p>Erro ao carregar aplicações</p>
                </div>
            `;
        }
    }

    async loadClientApplicationsData() {
        try {
            // Carregar dados para filtros
            this.companies = await api.getCompanies();
            this.applications = await api.getApplications();
            this.populateClientAppFilters();
            
            // Carregar aplicações dos clientes
            const clientApps = await api.getClientApplications(this.clientAppFilters);
            this.renderClientApplicationsList(clientApps);
        } catch (error) {
            document.getElementById('clientApplicationsList').innerHTML = `
                <div class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    <p>Erro ao carregar aplicações dos clientes</p>
                </div>
            `;
        }
    }

    populateClientAppFilters() {
        // Filtro de empresas
        const companyFilter = document.getElementById('filterClientCompany');
        if (companyFilter) {
            companyFilter.innerHTML = '<option value="">Todas as empresas</option>';
            this.companies.forEach(company => {
                companyFilter.innerHTML += `<option value="${company.id_empresa}">${company.razao_social}</option>`;
            });
        }

        // Filtro de aplicações
        const appFilter = document.getElementById('filterClientApplication');
        if (appFilter) {
            appFilter.innerHTML = '<option value="">Todas as aplicações</option>';
            this.applications.forEach(app => {
                appFilter.innerHTML += `<option value="${app.id_aplicacao}">${app.descricao}</option>`;
            });
        }

        // Selects do modal
        const companySelect = document.getElementById('clientAppCompany');
        const appSelect = document.getElementById('clientAppApplication');
        
        if (companySelect) {
            companySelect.innerHTML = '<option value="">Selecione uma empresa...</option>';
            this.companies.forEach(company => {
                companySelect.innerHTML += `<option value="${company.id_empresa}">${company.razao_social}</option>`;
            });
        }

        if (appSelect) {
            appSelect.innerHTML = '<option value="">Selecione uma aplicação...</option>';
            this.applications.forEach(app => {
                appSelect.innerHTML += `<option value="${app.id_aplicacao}">${app.descricao} (${app.tipo})</option>`;
            });
        }
    }

    renderApplicationsList(applications) {
        const container = document.getElementById('applicationsList');

        if (applications.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-app" style="font-size: 3rem;"></i>
                    <p class="mt-3">Nenhuma aplicação encontrada</p>
                    <button class="btn btn-primary" onclick="aplicacoesManager.showCreateModal()">
                        <i class="bi bi-plus-circle me-2"></i>Criar primeira aplicação
                    </button>
                </div>
            `;
            return;
        }

        const html = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Descrição</th>
                            <th>Tipo</th>
                            <th>APP_KEY</th>
                            <th>Clientes</th>
                            <th>Status</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${applications.map(app => `
                            <tr>
                                <td>
                                    <div class="fw-semibold">${app.descricao}</div>
                                    <small class="text-muted">ID: ${app.id_aplicacao}</small>
                                </td>
                                <td>
                                    <span class="badge bg-info">${app.tipo}</span>
                                </td>
                                <td>
                                    <code class="credential-display">${app.app_key}</code>
                                </td>
                                <td>
                                    <span class="badge bg-primary">${app.total_clientes || 0}</span>
                                </td>
                                <td>${formatStatus(app.ativo)}</td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-success" 
                                                onclick="aplicacoesManager.viewCredentials('${app.id_aplicacao}')"
                                                title="Ver credenciais">
                                            <i class="bi bi-key"></i>
                                        </button>
                                        <button class="btn btn-outline-warning" 
                                                onclick="aplicacoesManager.editApplication('${app.id_aplicacao}')"
                                                title="Editar">
                                            <i class="bi bi-pencil"></i>
                                        </button>
                                        <button class="btn btn-outline-info" 
                                                onclick="aplicacoesManager.rotateSecret('${app.id_aplicacao}')"
                                                title="Rotar secret">
                                            <i class="bi bi-arrow-clockwise"></i>
                                        </button>
                                        <button class="btn btn-outline-danger" 
                                                onclick="aplicacoesManager.deleteApplication('${app.id_aplicacao}')"
                                                title="Excluir">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = html;
    }

    renderClientApplicationsList(clientApps) {
        const container = document.getElementById('clientApplicationsList');

        if (clientApps.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-link-45deg" style="font-size: 3rem;"></i>
                    <p class="mt-3">Nenhuma aplicação vinculada encontrada</p>
                    <button class="btn btn-primary" onclick="aplicacoesManager.showCreateClientAppModal()">
                        <i class="bi bi-link me-2"></i>Vincular primeira aplicação
                    </button>
                </div>
            `;
            return;
        }

        const html = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Nome</th>
                            <th>Empresa</th>
                            <th>Aplicação</th>
                            <th>Tipo</th>
                            <th>Configurações</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${clientApps.map(clientApp => `
                            <tr>
                                <td>
                                    <div class="fw-semibold">${clientApp.nome_aplicacao}</div>
                                    <small class="text-muted">ID: ${clientApp.id_aplicacao_cliente}</small>
                                </td>
                                <td>
                                    <div class="fw-semibold">${clientApp.empresa?.razao_social || 'N/A'}</div>
                                    ${clientApp.empresa?.nome_fantasia ? `<small class="text-muted">${clientApp.empresa.nome_fantasia}</small>` : ''}
                                </td>
                                <td>
                                    <div class="fw-semibold">${clientApp.aplicacao?.descricao || 'N/A'}</div>
                                </td>
                                <td>
                                    <span class="badge bg-info">${clientApp.aplicacao?.tipo || 'N/A'}</span>
                                </td>
                                <td>
                                    <div class="d-flex gap-1">
                                        ${clientApp.config_omie_json ? '<span class="badge bg-success">Omie</span>' : ''}
                                        ${clientApp.config_aplicacao_json ? '<span class="badge bg-info">App</span>' : ''}
                                    </div>
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" 
                                                onclick="aplicacoesManager.viewClientApp('${clientApp.id_aplicacao_cliente}')"
                                                title="Visualizar">
                                            <i class="bi bi-eye"></i>
                                        </button>
                                        <button class="btn btn-outline-warning" 
                                                onclick="aplicacoesManager.editClientApp('${clientApp.id_aplicacao_cliente}')"
                                                title="Editar">
                                            <i class="bi bi-pencil"></i>
                                        </button>
                                        <button class="btn btn-outline-danger" 
                                                onclick="aplicacoesManager.deleteClientApp('${clientApp.id_aplicacao_cliente}')"
                                                title="Excluir">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = html;
    }

    // Métodos de aplicações do sistema
    showCreateModal() {
        this.currentApplication = null;
        document.getElementById('applicationModalTitle').textContent = 'Nova Aplicação';
        document.getElementById('applicationForm').reset();
        
        const modal = new bootstrap.Modal(document.getElementById('applicationModal'));
        modal.show();
    }

    async saveApplication() {
        const form = document.getElementById('applicationForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const data = {
            descricao: document.getElementById('appDescription').value.trim(),
            tipo: document.getElementById('appType').value,
            ativo: document.getElementById('appStatus').value === 'true'
        };

        try {
            if (this.currentApplication) {
                await api.updateApplication(this.currentApplication.id_aplicacao, data);
                showAlert('Aplicação atualizada com sucesso!', 'success');
            } else {
                const response = await api.createApplication(data.descricao, data.tipo);
                showAlert('Aplicação criada com sucesso!', 'success');
                
                // Mostrar credenciais da nova aplicação
                this.showNewApplicationCredentials(response);
            }

            // Fechar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('applicationModal'));
            modal.hide();
            
            // Recarregar lista
            await this.loadApplicationsData();
            
        } catch (error) {
            showAlert('Erro ao salvar aplicação: ' + error.message, 'danger');
        }
    }

    showNewApplicationCredentials(appData) {
        setTimeout(() => {
            const credentialsContent = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    <strong>IMPORTANTE:</strong> Guarde estas credenciais em local seguro. 
                    O APP_SECRET não será exibido novamente!
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <label class="form-label fw-bold">APP_KEY:</label>
                        <div class="input-group">
                            <input type="text" class="form-control credential-display" value="${appData.app_key}" readonly>
                            <button class="btn btn-outline-primary" onclick="copyToClipboard('${appData.app_key}')">
                                <i class="bi bi-clipboard"></i>
                            </button>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-bold">APP_SECRET:</label>
                        <div class="input-group">
                            <input type="text" class="form-control credential-display" value="${appData.app_secret}" readonly>
                            <button class="btn btn-outline-primary" onclick="copyToClipboard('${appData.app_secret}')">
                                <i class="bi bi-clipboard"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                <hr>
                
                <h6>Detalhes da Aplicação:</h6>
                <ul class="list-unstyled">
                    <li><strong>Descrição:</strong> ${appData.descricao}</li>
                    <li><strong>Tipo:</strong> ${appData.tipo}</li>
                    <li><strong>ID:</strong> ${appData.id_aplicacao}</li>
                </ul>
            `;

            document.getElementById('credentialsContent').innerHTML = credentialsContent;
            const modal = new bootstrap.Modal(document.getElementById('credentialsViewModal'));
            modal.show();
        }, 500);
    }

    async viewCredentials(id) {
        try {
            const app = await api.getApplication(id);
            
            const credentialsContent = `
                <div class="row">
                    <div class="col-md-6">
                        <label class="form-label fw-bold">APP_KEY:</label>
                        <div class="input-group">
                            <input type="text" class="form-control credential-display" value="${app.app_key}" readonly>
                            <button class="btn btn-outline-primary" onclick="copyToClipboard('${app.app_key}')">
                                <i class="bi bi-clipboard"></i>
                            </button>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-bold">APP_SECRET:</label>
                        <div class="input-group">
                            <input type="password" class="form-control" value="••••••••••••••••" readonly>
                            <button class="btn btn-outline-warning" onclick="aplicacoesManager.rotateSecret('${app.id_aplicacao}')">
                                <i class="bi bi-arrow-clockwise"></i> Rotar
                            </button>
                        </div>
                        <small class="text-muted">Use "Rotar Secret" para gerar um novo APP_SECRET</small>
                    </div>
                </div>
                
                <hr>
                
                <h6>Detalhes da Aplicação:</h6>
                <ul class="list-unstyled">
                    <li><strong>Descrição:</strong> ${app.descricao}</li>
                    <li><strong>Tipo:</strong> ${app.tipo}</li>
                    <li><strong>ID:</strong> ${app.id_aplicacao}</li>
                    <li><strong>Clientes:</strong> ${app.total_clientes || 0}</li>
                    <li><strong>Status:</strong> ${app.ativo ? 'Ativo' : 'Inativo'}</li>
                </ul>
            `;

            document.getElementById('credentialsContent').innerHTML = credentialsContent;
            const modal = new bootstrap.Modal(document.getElementById('credentialsViewModal'));
            modal.show();
            
        } catch (error) {
            showAlert('Erro ao carregar credenciais', 'danger');
        }
    }

    async rotateSecret(id) {
        if (!confirm('Tem certeza que deseja rotar o APP_SECRET? Isso invalidará o secret atual!')) {
            return;
        }

        try {
            const response = await api.rotateAppSecret(id);
            
            const credentialsContent = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    <strong>NOVO APP_SECRET GERADO!</strong> Atualize suas configurações com o novo secret.
                </div>
                
                <div class="row">
                    <div class="col-12">
                        <label class="form-label fw-bold">NOVO APP_SECRET:</label>
                        <div class="input-group">
                            <input type="text" class="form-control credential-display" value="${response.app_secret}" readonly>
                            <button class="btn btn-outline-primary" onclick="copyToClipboard('${response.app_secret}')">
                                <i class="bi bi-clipboard"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;

            document.getElementById('credentialsContent').innerHTML = credentialsContent;
            const modal = new bootstrap.Modal(document.getElementById('credentialsViewModal'));
            modal.show();
            
            showAlert('APP_SECRET rotacionado com sucesso!', 'success');
            
        } catch (error) {
            showAlert('Erro ao rotar APP_SECRET: ' + error.message, 'danger');
        }
    }

    // Métodos de aplicações dos clientes
    showCreateClientAppModal() {
        this.currentClientApp = null;
        document.getElementById('clientAppModalTitle').textContent = 'Vincular Aplicação';
        document.getElementById('clientAppForm').reset();
        
        const modal = new bootstrap.Modal(document.getElementById('clientAppModal'));
        modal.show();
    }

    async saveClientApplication() {
        const form = document.getElementById('clientAppForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const data = {
            nome_aplicacao: document.getElementById('clientAppName').value.trim(),
            id_empresa: document.getElementById('clientAppCompany').value,
            id_aplicacao: document.getElementById('clientAppApplication').value,
            config_omie_json: this.parseJsonField('clientAppOmieConfig'),
            config_aplicacao_json: this.parseJsonField('clientAppConfig')
        };

        try {
            if (this.currentClientApp) {
                await api.updateClientApplication(this.currentClientApp.id_aplicacao_cliente, data);
                showAlert('Aplicação atualizada com sucesso!', 'success');
            } else {
                await api.createClientApplication(data);
                showAlert('Aplicação vinculada com sucesso!', 'success');
            }

            // Fechar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('clientAppModal'));
            modal.hide();
            
            // Recarregar lista
            await this.loadClientApplicationsData();
            
        } catch (error) {
            showAlert('Erro ao salvar aplicação: ' + error.message, 'danger');
        }
    }

    parseJsonField(fieldId) {
        const value = document.getElementById(fieldId).value.trim();
        if (!value) return null;
        
        try {
            return JSON.parse(value);
        } catch (error) {
            throw new Error(`JSON inválido no campo ${fieldId}`);
        }
    }

    // Métodos de filtro e busca
    search() {
        this.filters.search = document.getElementById('searchApplications').value.trim();
        this.loadApplicationsData();
    }

    filterByType() {
        this.filters.tipo = document.getElementById('filterAppType').value || null;
        this.loadApplicationsData();
    }

    clearFilters() {
        this.filters = { search: '', tipo: null };
        document.getElementById('searchApplications').value = '';
        document.getElementById('filterAppType').value = '';
        this.loadApplicationsData();
    }

    searchClientApps() {
        this.clientAppFilters.search = document.getElementById('searchClientApps').value.trim();
        this.loadClientApplicationsData();
    }

    filterClientAppsByCompany() {
        this.clientAppFilters.id_empresa = document.getElementById('filterClientCompany').value || null;
        this.loadClientApplicationsData();
    }

    filterClientAppsByApplication() {
        this.clientAppFilters.id_aplicacao = document.getElementById('filterClientApplication').value || null;
        this.loadClientApplicationsData();
    }

    clearClientAppFilters() {
        this.clientAppFilters = { search: '', id_empresa: null, id_aplicacao: null };
        document.getElementById('searchClientApps').value = '';
        document.getElementById('filterClientCompany').value = '';
        document.getElementById('filterClientApplication').value = '';
        this.loadClientApplicationsData();
    }
}

// Instância global
const aplicacoesManager = new AplicacoesManager();
const aplicacoesClienteManager = aplicacoesManager; // Alias para compatibilidade