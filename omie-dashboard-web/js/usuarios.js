/**
 * Módulo de Gestão de Usuários
 */

class UsuariosManager {
    constructor() {
        this.currentUser = null;
        this.filters = {
            search: '',
            id_empresa: null,
            ativo: null
        };
        this.companies = [];
    }

    async loadUsuarios() {
        const content = document.getElementById('content');
        
        content.innerHTML = `
            <div class="fade-in">
                <!-- Header -->
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h2><i class="bi bi-people me-2"></i>Usuários</h2>
                        <p class="text-muted mb-0">Gestão de usuários do sistema</p>
                    </div>
                    <div>
                        <button class="btn btn-primary" onclick="usuariosManager.showCreateModal()">
                            <i class="bi bi-person-plus me-2"></i>Novo Usuário
                        </button>
                    </div>
                </div>

                <!-- Filtros -->
                <div class="card mb-4">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="input-group">
                                    <input type="text" class="form-control" id="searchUsers" 
                                           placeholder="Buscar por nome ou email...">
                                    <button class="btn btn-outline-primary" onclick="usuariosManager.search()">
                                        <i class="bi bi-search"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <select class="form-select" id="filterCompany" onchange="usuariosManager.filterByCompany()">
                                    <option value="">Todas as empresas</option>
                                </select>
                            </div>
                            <div class="col-md-2">
                                <select class="form-select" id="filterUserStatus" onchange="usuariosManager.filterByStatus()">
                                    <option value="">Todos os status</option>
                                    <option value="true">Ativo</option>
                                    <option value="false">Inativo</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <button class="btn btn-outline-secondary w-100" onclick="usuariosManager.clearFilters()">
                                    <i class="bi bi-x-circle me-1"></i>Limpar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Lista de Usuários -->
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="bi bi-list me-2"></i>Usuários Cadastrados</h6>
                    </div>
                    <div class="card-body">
                        <div id="usersList">
                            <div class="text-center">
                                <div class="spinner-border"></div>
                                <p class="mt-2">Carregando usuários...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal Criar/Editar Usuário -->
            <div class="modal fade" id="userModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="userModalTitle">Novo Usuário</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="userForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="userName" class="form-label">Nome *</label>
                                            <input type="text" class="form-control" id="userName" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="userSobrenome" class="form-label">Sobrenome *</label>
                                            <input type="text" class="form-control" id="userSobrenome" required>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="userEmail" class="form-label">E-mail *</label>
                                    <input type="email" class="form-control" id="userEmail" required>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="userCompany" class="form-label">Empresa *</label>
                                            <select class="form-select" id="userCompany" required>
                                                <option value="">Selecione uma empresa...</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="userTelefone" class="form-label">Telefone</label>
                                            <input type="tel" class="form-control" id="userTelefone">
                                        </div>
                                    </div>
                                </div>

                                <div class="mb-3">
                                    <label for="userStatus" class="form-label">Status</label>
                                    <select class="form-select" id="userStatus">
                                        <option value="true">Ativo</option>
                                        <option value="false">Inativo</option>
                                    </select>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="usuariosManager.saveUser()">
                                <i class="bi bi-check-circle me-1"></i>Salvar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Carregar dados
        await this.loadInitialData();
    }

    async loadInitialData() {
        try {
            // Carregar empresas para filtros e formulário
            this.companies = await api.getCompanies();
            this.populateCompanySelects();
            
            // Carregar usuários
            await this.loadUsersData();
        } catch (error) {
            console.error('Erro ao carregar dados iniciais:', error);
        }
    }

    populateCompanySelects() {
        const filterSelect = document.getElementById('filterCompany');
        const formSelect = document.getElementById('userCompany');

        // Limpar options existentes (exceto o primeiro)
        if (filterSelect) {
            filterSelect.innerHTML = '<option value="">Todas as empresas</option>';
            this.companies.forEach(company => {
                filterSelect.innerHTML += `<option value="${company.id_empresa}">${company.razao_social}</option>`;
            });
        }

        if (formSelect) {
            formSelect.innerHTML = '<option value="">Selecione uma empresa...</option>';
            this.companies.forEach(company => {
                formSelect.innerHTML += `<option value="${company.id_empresa}">${company.razao_social}</option>`;
            });
        }
    }

    async loadUsersData() {
        try {
            const users = await api.getUsers(this.filters);
            this.renderUsersList(users);
        } catch (error) {
            document.getElementById('usersList').innerHTML = `
                <div class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    <p>Erro ao carregar usuários</p>
                </div>
            `;
        }
    }

    renderUsersList(users) {
        const container = document.getElementById('usersList');

        if (users.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-people" style="font-size: 3rem;"></i>
                    <p class="mt-3">Nenhum usuário encontrado</p>
                    <button class="btn btn-primary" onclick="usuariosManager.showCreateModal()">
                        <i class="bi bi-person-plus me-2"></i>Criar primeiro usuário
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
                            <th>E-mail</th>
                            <th>Empresa</th>
                            <th>Telefone</th>
                            <th>Status</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${users.map(user => `
                            <tr>
                                <td>
                                    <div class="d-flex align-items-center">
                                        <div class="me-3">
                                            <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" 
                                                 style="width: 40px; height: 40px; font-weight: 600;">
                                                ${user.nome.charAt(0).toUpperCase()}
                                            </div>
                                        </div>
                                        <div>
                                            <div class="fw-semibold">${user.nome} ${user.sobrenome || ''}</div>
                                        </div>
                                    </div>
                                </td>
                                <td>${user.email}</td>
                                <td>
                                    <div class="fw-semibold">${user.empresa?.razao_social || 'N/A'}</div>
                                    ${user.empresa?.nome_fantasia ? `<small class="text-muted">${user.empresa.nome_fantasia}</small>` : ''}
                                </td>
                                <td>${user.telefone || '-'}</td>
                                <td>${formatStatus(user.ativo)}</td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" 
                                                onclick="usuariosManager.viewUser('${user.id_usuario}')"
                                                title="Visualizar">
                                            <i class="bi bi-eye"></i>
                                        </button>
                                        <button class="btn btn-outline-warning" 
                                                onclick="usuariosManager.editUser('${user.id_usuario}')"
                                                title="Editar">
                                            <i class="bi bi-pencil"></i>
                                        </button>
                                        <button class="btn btn-outline-danger" 
                                                onclick="usuariosManager.deleteUser('${user.id_usuario}')"
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
        this.currentUser = null;
        document.getElementById('userModalTitle').textContent = 'Novo Usuário';
        document.getElementById('userForm').reset();
        
        const modal = new bootstrap.Modal(document.getElementById('userModal'));
        modal.show();
    }

    async editUser(id) {
        try {
            const user = await api.getUser(id);
            this.currentUser = user;
            
            // Preencher formulário
            document.getElementById('userModalTitle').textContent = 'Editar Usuário';
            document.getElementById('userName').value = user.nome || '';
            document.getElementById('userSobrenome').value = user.sobrenome || '';
            document.getElementById('userEmail').value = user.email || '';
            document.getElementById('userCompany').value = user.id_empresa || '';
            document.getElementById('userTelefone').value = user.telefone || '';
            document.getElementById('userStatus').value = user.ativo.toString();
            
            const modal = new bootstrap.Modal(document.getElementById('userModal'));
            modal.show();
            
        } catch (error) {
            showAlert('Erro ao carregar dados do usuário', 'danger');
        }
    }

    async saveUser() {
        const form = document.getElementById('userForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const data = {
            nome: document.getElementById('userName').value.trim(),
            sobrenome: document.getElementById('userSobrenome').value.trim(),
            email: document.getElementById('userEmail').value.trim(),
            id_empresa: document.getElementById('userCompany').value,
            telefone: document.getElementById('userTelefone').value.trim() || null,
            ativo: document.getElementById('userStatus').value === 'true'
        };

        try {
            if (this.currentUser) {
                await api.updateUser(this.currentUser.id_usuario, data);
                showAlert('Usuário atualizado com sucesso!', 'success');
            } else {
                await api.createUser(data);
                showAlert('Usuário criado com sucesso!', 'success');
            }

            // Fechar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('userModal'));
            modal.hide();
            
            // Recarregar lista
            await this.loadUsersData();
            
        } catch (error) {
            console.error('Erro ao salvar usuário:', error);
            let errorMessage = 'Erro desconhecido';
            
            if (error.message) {
                errorMessage = error.message;
            } else if (typeof error === 'object') {
                errorMessage = JSON.stringify(error);
            }
            
            showAlert('Erro ao salvar usuário: ' + errorMessage, 'danger');
        }
    }

    async deleteUser(id) {
        if (!confirm('Tem certeza que deseja excluir este usuário?')) {
            return;
        }

        try {
            await api.deleteUser(id);
            showAlert('Usuário excluído com sucesso!', 'success');
            await this.loadUsersData();
        } catch (error) {
            showAlert('Erro ao excluir usuário: ' + error.message, 'danger');
        }
    }

    async viewUser(id) {
        try {
            const user = await api.getUser(id);
            
            // Implementar modal de visualização
            showAlert('Funcionalidade de visualização em desenvolvimento', 'info');
            
        } catch (error) {
            showAlert('Erro ao carregar usuário', 'danger');
        }
    }

    search() {
        this.filters.search = document.getElementById('searchUsers').value.trim();
        this.loadUsersData();
    }

    filterByCompany() {
        const companyId = document.getElementById('filterCompany').value;
        this.filters.id_empresa = companyId || null;
        this.loadUsersData();
    }

    filterByStatus() {
        const status = document.getElementById('filterUserStatus').value;
        this.filters.ativo = status === '' ? null : status === 'true';
        this.loadUsersData();
    }

    clearFilters() {
        this.filters = { search: '', id_empresa: null, ativo: null };
        document.getElementById('searchUsers').value = '';
        document.getElementById('filterCompany').value = '';
        document.getElementById('filterUserStatus').value = '';
        this.loadUsersData();
    }
}

// Instância global
const usuariosManager = new UsuariosManager();