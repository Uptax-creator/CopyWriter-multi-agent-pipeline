/**
 * Módulo do Dashboard Principal
 */

class Dashboard {
    constructor() {
        this.metrics = {
            empresas: 0,
            usuarios: 0,
            aplicacoes: 0,
            aplicacoesCliente: 0
        };
    }

    async loadDashboard() {
        const content = document.getElementById('content');
        
        content.innerHTML = `
            <div class="fade-in">
                <!-- Header -->
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h2><i class="bi bi-speedometer2 me-2"></i>Dashboard</h2>
                        <p class="text-muted mb-0">Visão geral do sistema</p>
                    </div>
                    <div>
                        <button class="btn btn-primary btn-sm" onclick="dashboard.refreshMetrics()">
                            <i class="bi bi-arrow-clockwise me-1"></i>Atualizar
                        </button>
                    </div>
                </div>

                <!-- Métricas -->
                <div class="row mb-4">
                    <div class="col-md-3 col-sm-6 mb-3">
                        <div class="card metric-card">
                            <div class="card-body text-center">
                                <div class="metric-icon text-primary mb-2">
                                    <i class="bi bi-building"></i>
                                </div>
                                <div class="metric-value text-primary" id="metricEmpresas">-</div>
                                <div class="metric-label">Empresas</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-3 col-sm-6 mb-3">
                        <div class="card metric-card">
                            <div class="card-body text-center">
                                <div class="metric-icon text-success mb-2">
                                    <i class="bi bi-people"></i>
                                </div>
                                <div class="metric-value text-success" id="metricUsuarios">-</div>
                                <div class="metric-label">Usuários</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-3 col-sm-6 mb-3">
                        <div class="card metric-card">
                            <div class="card-body text-center">
                                <div class="metric-icon text-info mb-2">
                                    <i class="bi bi-app"></i>
                                </div>
                                <div class="metric-value text-info" id="metricAplicacoes">-</div>
                                <div class="metric-label">Aplicações</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-3 col-sm-6 mb-3">
                        <div class="card metric-card">
                            <div class="card-body text-center">
                                <div class="metric-icon text-warning mb-2">
                                    <i class="bi bi-link-45deg"></i>
                                </div>
                                <div class="metric-value text-warning" id="metricAplicacoesCliente">-</div>
                                <div class="metric-label">Apps Clientes</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Ações Rápidas -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0"><i class="bi bi-lightning me-2"></i>Ações Rápidas</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-3 col-sm-6 mb-3">
                                        <button class="btn btn-outline-primary w-100" onclick="showSection('empresas'); empresasManager.showCreateModal()">
                                            <i class="bi bi-building-add d-block mb-2" style="font-size: 1.5rem;"></i>
                                            Nova Empresa
                                        </button>
                                    </div>
                                    <div class="col-md-3 col-sm-6 mb-3">
                                        <button class="btn btn-outline-success w-100" onclick="showSection('usuarios'); usuariosManager.showCreateModal()">
                                            <i class="bi bi-person-plus d-block mb-2" style="font-size: 1.5rem;"></i>
                                            Novo Usuário
                                        </button>
                                    </div>
                                    <div class="col-md-3 col-sm-6 mb-3">
                                        <button class="btn btn-outline-info w-100" onclick="showSection('aplicacoes'); aplicacoesManager.showCreateModal()">
                                            <i class="bi bi-app-indicator d-block mb-2" style="font-size: 1.5rem;"></i>
                                            Nova Aplicação
                                        </button>
                                    </div>
                                    <div class="col-md-3 col-sm-6 mb-3">
                                        <button class="btn btn-outline-warning w-100" onclick="showSection('aplicacoes-cliente'); aplicacoesClienteManager.showCreateModal()">
                                            <i class="bi bi-link d-block mb-2" style="font-size: 1.5rem;"></i>
                                            Vincular App
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Resumo das Entidades -->
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h6 class="mb-0"><i class="bi bi-building me-2"></i>Empresas Recentes</h6>
                                <a href="#" class="btn btn-sm btn-outline-primary" onclick="showSection('empresas')">Ver todas</a>
                            </div>
                            <div class="card-body">
                                <div id="recentCompanies">
                                    <div class="text-center text-muted">
                                        <div class="spinner-border spinner-border-sm me-2"></div>
                                        Carregando...
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6 mb-4">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h6 class="mb-0"><i class="bi bi-app me-2"></i>Aplicações do Sistema</h6>
                                <a href="#" class="btn btn-sm btn-outline-info" onclick="showSection('aplicacoes')">Ver todas</a>
                            </div>
                            <div class="card-body">
                                <div id="recentApplications">
                                    <div class="text-center text-muted">
                                        <div class="spinner-border spinner-border-sm me-2"></div>
                                        Carregando...
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Status do Sistema -->
                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0"><i class="bi bi-heart-pulse me-2"></i>Status do Sistema</h6>
                            </div>
                            <div class="card-body">
                                <div id="systemStatus">
                                    <div class="text-center text-muted">
                                        <div class="spinner-border spinner-border-sm me-2"></div>
                                        Verificando status...
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Carregar dados
        await this.loadData();
    }

    async loadData() {
        try {
            // Carregar métricas
            await this.loadMetrics();
            
            // Carregar empresas recentes
            await this.loadRecentCompanies();
            
            // Carregar aplicações
            await this.loadRecentApplications();
            
            // Verificar status do sistema
            await this.checkSystemStatus();
            
        } catch (error) {
            console.error('Erro ao carregar dados do dashboard:', error);
        }
    }

    async loadMetrics() {
        try {
            // Carregar dados em paralelo
            const [empresas, usuarios, aplicacoes, aplicacoesCliente] = await Promise.all([
                api.getCompanies(),
                api.getUsers(),
                api.getApplications(),
                api.getClientApplications()
            ]);

            // Atualizar métricas
            this.metrics = {
                empresas: empresas.length,
                usuarios: usuarios.length,
                aplicacoes: aplicacoes.length,
                aplicacoesCliente: aplicacoesCliente.length
            };

            // Atualizar UI
            document.getElementById('metricEmpresas').textContent = this.metrics.empresas;
            document.getElementById('metricUsuarios').textContent = this.metrics.usuarios;
            document.getElementById('metricAplicacoes').textContent = this.metrics.aplicacoes;
            document.getElementById('metricAplicacoesCliente').textContent = this.metrics.aplicacoesCliente;

        } catch (error) {
            console.error('Erro ao carregar métricas:', error);
            // Mostrar zeros em caso de erro
            document.getElementById('metricEmpresas').textContent = '0';
            document.getElementById('metricUsuarios').textContent = '0';
            document.getElementById('metricAplicacoes').textContent = '0';
            document.getElementById('metricAplicacoesCliente').textContent = '0';
        }
    }

    async loadRecentCompanies() {
        try {
            const companies = await api.getCompanies({ limit: 5 });
            const container = document.getElementById('recentCompanies');

            if (companies.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="bi bi-building me-2"></i>Nenhuma empresa cadastrada
                    </div>
                `;
                return;
            }

            const html = companies.map(company => `
                <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                    <div>
                        <div class="fw-semibold">${company.razao_social}</div>
                        <small class="text-muted">${formatCNPJ(company.cnpj)}</small>
                    </div>
                    <div>
                        ${formatStatus(company.ativo)}
                    </div>
                </div>
            `).join('');

            container.innerHTML = html;

        } catch (error) {
            console.error('Erro ao carregar empresas recentes:', error);
            document.getElementById('recentCompanies').innerHTML = `
                <div class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>Erro ao carregar
                </div>
            `;
        }
    }

    async loadRecentApplications() {
        try {
            const applications = await api.getApplications();
            const container = document.getElementById('recentApplications');

            if (applications.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="bi bi-app me-2"></i>Nenhuma aplicação cadastrada
                    </div>
                `;
                return;
            }

            const html = applications.slice(0, 5).map(app => `
                <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                    <div>
                        <div class="fw-semibold">${app.descricao}</div>
                        <small class="text-muted">
                            <i class="bi bi-tag me-1"></i>${app.tipo}
                            <span class="ms-2">
                                <i class="bi bi-people me-1"></i>${app.total_clientes} clientes
                            </span>
                        </small>
                    </div>
                    <div>
                        ${formatStatus(app.ativo)}
                    </div>
                </div>
            `).join('');

            container.innerHTML = html;

        } catch (error) {
            console.error('Erro ao carregar aplicações:', error);
            document.getElementById('recentApplications').innerHTML = `
                <div class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>Erro ao carregar
                </div>
            `;
        }
    }

    async checkSystemStatus() {
        try {
            const health = await api.healthCheck();
            const container = document.getElementById('systemStatus');

            container.innerHTML = `
                <div class="row">
                    <div class="col-md-4">
                        <div class="d-flex align-items-center">
                            <i class="bi bi-check-circle-fill text-success me-2"></i>
                            <div>
                                <div class="fw-semibold">API Status</div>
                                <small class="text-muted">${health.status}</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="d-flex align-items-center">
                            <i class="bi bi-server text-info me-2"></i>
                            <div>
                                <div class="fw-semibold">Serviço</div>
                                <small class="text-muted">${health.service}</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="d-flex align-items-center">
                            <i class="bi bi-tag text-secondary me-2"></i>
                            <div>
                                <div class="fw-semibold">Versão</div>
                                <small class="text-muted">${health.version}</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;

        } catch (error) {
            console.error('Erro ao verificar status do sistema:', error);
            document.getElementById('systemStatus').innerHTML = `
                <div class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Erro ao verificar status do sistema
                </div>
            `;
        }
    }

    async refreshMetrics() {
        showAlert('Atualizando dados...', 'info', 1000);
        await this.loadData();
        showAlert('Dados atualizados!', 'success', 2000);
    }
}

// Instância global do dashboard
const dashboard = new Dashboard();