/**
 * Módulo de Gestão de Empresas
 */

class EmpresasManager {
    constructor() {
        this.currentCompany = null;
        this.filters = {
            search: '',
            ativo: null
        };
    }

    async loadEmpresas() {
        const content = document.getElementById('content');
        
        content.innerHTML = `
            <div class="fade-in">
                <!-- Header -->
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h2><i class="bi bi-building me-2"></i>Empresas</h2>
                        <p class="text-muted mb-0">Gestão de empresas cadastradas</p>
                    </div>
                    <div>
                        <button class="btn btn-primary" onclick="empresasManager.showCreateModal()">
                            <i class="bi bi-plus-circle me-2"></i>Nova Empresa
                        </button>
                    </div>
                </div>

                <!-- Filtros -->
                <div class="card mb-4">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="input-group">
                                    <input type="text" class="form-control" id="searchCompanies" 
                                           placeholder="Buscar por razão social ou CNPJ...">
                                    <button class="btn btn-outline-primary" onclick="empresasManager.search()">
                                        <i class="bi bi-search"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <select class="form-select" id="filterStatus" onchange="empresasManager.filterByStatus()">
                                    <option value="">Todos os status</option>
                                    <option value="true">Ativo</option>
                                    <option value="false">Inativo</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <button class="btn btn-outline-secondary w-100" onclick="empresasManager.clearFilters()">
                                    <i class="bi bi-x-circle me-1"></i>Limpar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Lista de Empresas -->
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="bi bi-list me-2"></i>Empresas Cadastradas</h6>
                    </div>
                    <div class="card-body">
                        <div id="companiesList">
                            <div class="text-center">
                                <div class="spinner-border"></div>
                                <p class="mt-2">Carregando empresas...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal Criar/Editar Empresa -->
            <div class="modal fade" id="companyModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="companyModalTitle">Nova Empresa</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="companyForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="companyRazaoSocial" class="form-label">Razão Social *</label>
                                            <input type="text" class="form-control" id="companyRazaoSocial" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="companyCnpj" class="form-label">CNPJ *</label>
                                            <input type="text" class="form-control" id="companyCnpj" 
                                                   pattern="[0-9]{2}.[0-9]{3}.[0-9]{3}/[0-9]{4}-[0-9]{2}" 
                                                   placeholder="00.000.000/0000-00" required>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="companyNomeFantasia" class="form-label">Nome Fantasia</label>
                                            <input type="text" class="form-control" id="companyNomeFantasia">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="companyEmail" class="form-label">E-mail</label>
                                            <input type="email" class="form-control" id="companyEmail">
                                        </div>
                                    </div>
                                </div>

                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="companyTelefone" class="form-label">Telefone</label>
                                            <input type="tel" class="form-control" id="companyTelefone">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="companyStatus" class="form-label">Status</label>
                                            <select class="form-select" id="companyStatus">
                                                <option value="true">Ativo</option>
                                                <option value="false">Inativo</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                <div class="mb-3">
                                    <label for="companyEndereco" class="form-label">Endereço</label>
                                    <textarea class="form-control" id="companyEndereco" rows="2"></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="empresasManager.saveCompany()">
                                <i class="bi bi-check-circle me-1"></i>Salvar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Carregar dados
        await this.loadCompaniesData();
    }

    async loadCompaniesData() {
        try {
            const companies = await api.getCompanies(this.filters);
            this.renderCompaniesList(companies);
        } catch (error) {
            document.getElementById('companiesList').innerHTML = `
                <div class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    <p>Erro ao carregar empresas</p>
                </div>
            `;
        }
    }

    renderCompaniesList(companies) {
        const container = document.getElementById('companiesList');

        if (companies.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-building" style="font-size: 3rem;"></i>
                    <p class="mt-3">Nenhuma empresa encontrada</p>
                    <button class="btn btn-primary" onclick="empresasManager.showCreateModal()">
                        <i class="bi bi-plus-circle me-2"></i>Criar primeira empresa
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
                            <th>Razão Social</th>
                            <th>CNPJ</th>
                            <th>E-mail</th>
                            <th>Status</th>
                            <th>Usuários</th>
                            <th>Aplicações</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${companies.map(company => `
                            <tr>
                                <td>
                                    <div class="fw-semibold">${company.razao_social}</div>
                                    ${company.nome_fantasia ? `<small class="text-muted">${company.nome_fantasia}</small>` : ''}
                                </td>
                                <td>${formatCNPJ(company.cnpj)}</td>
                                <td>${company.email || '-'}</td>
                                <td>${formatStatus(company.ativo)}</td>
                                <td>
                                    <span class="badge bg-primary">${company.total_usuarios || 0}</span>
                                </td>
                                <td>
                                    <span class="badge bg-info">${company.total_aplicacoes || 0}</span>
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" 
                                                onclick="empresasManager.viewCompany('${company.id_empresa}')"
                                                title="Visualizar">
                                            <i class="bi bi-eye"></i>
                                        </button>
                                        <button class="btn btn-outline-warning" 
                                                onclick="empresasManager.editCompany('${company.id_empresa}')"
                                                title="Editar">
                                            <i class="bi bi-pencil"></i>
                                        </button>
                                        <button class="btn btn-outline-danger" 
                                                onclick="empresasManager.deleteCompany('${company.id_empresa}')"
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

    showCreateModal() {
        this.currentCompany = null;
        document.getElementById('companyModalTitle').textContent = 'Nova Empresa';
        document.getElementById('companyForm').reset();
        
        const modal = new bootstrap.Modal(document.getElementById('companyModal'));
        modal.show();
    }

    async editCompany(id) {
        try {
            const company = await api.getCompany(id);
            this.currentCompany = company;
            
            // Preencher formulário
            document.getElementById('companyModalTitle').textContent = 'Editar Empresa';
            document.getElementById('companyRazaoSocial').value = company.razao_social || '';
            document.getElementById('companyCnpj').value = company.cnpj || '';
            document.getElementById('companyNomeFantasia').value = company.nome_fantasia || '';
            document.getElementById('companyEmail').value = company.email || '';
            document.getElementById('companyTelefone').value = company.telefone || '';
            document.getElementById('companyEndereco').value = company.endereco || '';
            document.getElementById('companyStatus').value = company.ativo.toString();
            
            const modal = new bootstrap.Modal(document.getElementById('companyModal'));
            modal.show();
            
        } catch (error) {
            showAlert('Erro ao carregar dados da empresa', 'danger');
        }
    }

    async saveCompany() {
        const form = document.getElementById('companyForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const data = {
            razao_social: document.getElementById('companyRazaoSocial').value.trim(),
            cnpj: document.getElementById('companyCnpj').value.replace(/\D/g, ''),
            nome_fantasia: document.getElementById('companyNomeFantasia').value.trim() || null,
            email: document.getElementById('companyEmail').value.trim() || null,
            telefone: document.getElementById('companyTelefone').value.trim() || null,
            endereco: document.getElementById('companyEndereco').value.trim() || null,
            ativo: document.getElementById('companyStatus').value === 'true'
        };

        try {
            if (this.currentCompany) {
                await api.updateCompany(this.currentCompany.id_empresa, data);
                showAlert('Empresa atualizada com sucesso!', 'success');
            } else {
                await api.createCompany(data);
                showAlert('Empresa criada com sucesso!', 'success');
            }

            // Fechar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('companyModal'));
            modal.hide();
            
            // Recarregar lista
            await this.loadCompaniesData();
            
        } catch (error) {
            showAlert('Erro ao salvar empresa: ' + error.message, 'danger');
        }
    }

    async deleteCompany(id) {
        if (!confirm('Tem certeza que deseja excluir esta empresa?')) {
            return;
        }

        try {
            await api.deleteCompany(id);
            showAlert('Empresa excluída com sucesso!', 'success');
            await this.loadCompaniesData();
        } catch (error) {
            showAlert('Erro ao excluir empresa: ' + error.message, 'danger');
        }
    }

    async viewCompany(id) {
        try {
            const company = await api.getCompany(id);
            
            // Implementar modal de visualização
            showAlert('Funcionalidade de visualização em desenvolvimento', 'info');
            
        } catch (error) {
            showAlert('Erro ao carregar empresa', 'danger');
        }
    }

    search() {
        this.filters.search = document.getElementById('searchCompanies').value.trim();
        this.loadCompaniesData();
    }

    filterByStatus() {
        const status = document.getElementById('filterStatus').value;
        this.filters.ativo = status === '' ? null : status === 'true';
        this.loadCompaniesData();
    }

    clearFilters() {
        this.filters = { search: '', ativo: null };
        document.getElementById('searchCompanies').value = '';
        document.getElementById('filterStatus').value = '';
        this.loadCompaniesData();
    }
}

// Instância global
const empresasManager = new EmpresasManager();