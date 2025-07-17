/**
 * Sistema de Autenticação v2.0
 * Gerencia login/cadastro com email/senha
 */

// Variável global para o AuthManager
let authManager = null;

class AuthManager {
    constructor() {
        this.currentUser = null;
        this.currentCompany = null;
        this.backend = null;
        
        // Verificar se securityManager está disponível
        this.checkSecurityManager();
        
        // Inicializar backend integration
        this.initBackend();
        
        this.init();
    }

    initBackend() {
        try {
            this.backend = new BackendIntegration();
            console.log('✅ Backend integration inicializada');
        } catch (error) {
            console.warn('⚠️ Erro ao inicializar backend integration:', error);
            this.backend = null;
        }
    }

    checkSecurityManager() {
        if (typeof securityManager === 'undefined') {
            console.warn('⚠️ SecurityManager não encontrado. Funcionalidades de segurança avançadas serão desabilitadas.');
            console.log('🔧 Usando fallbacks básicos para autenticação');
        } else {
            console.log('✅ SecurityManager carregado com sucesso');
        }
    }

    init() {
        // Verificar se já está logado (método seguro)
        try {
            const token = this.getStoredToken();
            if (token) {
                const userData = localStorage.getItem('user_data');
                if (userData) {
                    this.currentUser = JSON.parse(userData);
                    this.showCompanySelection();
                } else {
                    this.showWelcome();
                }
            } else {
                this.showWelcome();
            }
        } catch (error) {
            console.error('Erro ao verificar token:', error);
            this.showWelcome();
        }

        this.setupEventListeners();
    }

    // Método auxiliar para verificar token sem depender do securityManager ainda
    getStoredToken() {
        if (typeof securityManager !== 'undefined') {
            return securityManager.getSecureToken();
        } else {
            // Fallback simples se securityManager não estiver carregado
            return sessionStorage.getItem('secure_token');
        }
    }

    setupEventListeners() {
        console.log('🔧 Configurando event listeners...');
        
        // Form de cadastro
        const registerForm = document.getElementById('registerForm');
        console.log('📋 Formulário de cadastro encontrado:', !!registerForm);
        
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                console.log('🚀 Submit do formulário disparado!');
                e.preventDefault();
                console.log('📝 Chamando handleRegister...');
                this.handleRegister();
            });
        }

        // Form de login
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        // Validação de senhas em tempo real
        const senha = document.getElementById('registerSenha');
        const confirmarSenha = document.getElementById('registerConfirmarSenha');
        
        if (senha) {
            senha.addEventListener('input', () => {
                try {
                    this.updatePasswordStrength(senha.value);
                } catch (error) {
                    console.error('Erro ao validar senha:', error);
                }
            });
        }
        
        if (confirmarSenha) {
            confirmarSenha.addEventListener('input', () => {
                if (senha.value !== confirmarSenha.value) {
                    confirmarSenha.setCustomValidity('Senhas não coincidem');
                } else {
                    confirmarSenha.setCustomValidity('');
                }
            });
        }

        // Formatação automática de telefone
        this.setupPhoneFormatting();
    }

    async handleRegister() {
        console.log('📝 handleRegister() iniciado');
        
        try {
            const nome = document.getElementById('registerNome').value.trim();
            const sobrenome = document.getElementById('registerSobrenome').value.trim();
            const email = document.getElementById('registerEmail').value.trim().toLowerCase();
            const telefone = document.getElementById('registerTelefone').value.trim();
            const senha = document.getElementById('registerSenha').value;
            const confirmarSenha = document.getElementById('registerConfirmarSenha').value;
            
            console.log('📊 Dados coletados:', { nome, sobrenome, email, telefone: telefone ? 'preenchido' : 'vazio' });

            // Validações básicas
            if (senha !== confirmarSenha) {
                console.log('❌ Senhas não coincidem');
                this.showAlert('Senhas não coincidem', 'danger');
                return;
            }

        // Validação robusta de senha
        if (typeof securityManager !== 'undefined' && securityManager.validatePassword) {
            const passwordValidation = securityManager.validatePassword(senha);
            if (!passwordValidation.isValid) {
                this.showAlert('Senha não atende aos critérios de segurança:<br>' + 
                    passwordValidation.errors.join('<br>'), 'danger');
                return;
            }
        } else {
            // Validação básica se securityManager não estiver disponível
            console.log('⚠️ SecurityManager não disponível, usando validação básica');
            if (senha.length < 8) {
                this.showAlert('Senha deve ter pelo menos 8 caracteres', 'danger');
                return;
            }
            // Validação mínima adicional
            if (!/[A-Z]/.test(senha) || !/[a-z]/.test(senha) || !/[0-9]/.test(senha)) {
                this.showAlert('Senha deve conter pelo menos uma letra maiúscula, uma minúscula e um número', 'danger');
                return;
            }
        }

        // Validação de email
        if (!this.validateEmail(email)) {
            this.showAlert('E-mail inválido', 'danger');
            return;
        }

        // Validar email único (se validationManager estiver disponível)
        if (typeof validationManager !== 'undefined') {
            const emailValidation = await validationManager.validateEmailUnique(email);
            if (!emailValidation.valid) {
                this.showAlert(emailValidation.message, 'danger');
                return;
            }
        }

        // Combinar telefone com código do país
        const countryCode = document.getElementById('countryCode').value;
        const fullPhone = telefone ? `${countryCode} ${telefone}` : null;

        const userData = {
            nome,
            sobrenome,
            email,
            telefone: fullPhone,
            senha
        };

        try {
            this.showLoading(true);
            
            // Tentar registrar no backend primeiro
            if (this.backend) {
                console.log('📝 Registrando usuário no backend...');
                try {
                    const response = await this.backend.register(userData);
                    
                    if (response.success && response.user) {
                        this.currentUser = response.user;
                        
                        // Armazenar token se fornecido
                        if (response.token) {
                            if (typeof securityManager !== 'undefined') {
                                securityManager.storeTokenSecurely(response.token);
                            } else {
                                sessionStorage.setItem('secure_token', response.token);
                            }
                        }
                        
                        this.showAlert('Conta criada com sucesso no servidor!', 'success');
                        
                        setTimeout(() => {
                            this.showCompanySelection();
                        }, 1500);
                        
                        return; // Sucesso no backend, não executar fallback
                    }
                } catch (backendError) {
                    console.warn('⚠️ Erro no backend, usando fallback:', backendError.message);
                }
            }
            
            // Fallback para simulação local
            console.log('🔄 Usando registro simulado...');
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            this.currentUser = {
                id: 'user-' + Date.now(),
                nome,
                sobrenome,
                email,
                telefone
            };

            // Gerar token seguro
            if (typeof securityManager !== 'undefined' && securityManager.generateSecureToken) {
                const secureToken = securityManager.generateSecureToken();
                securityManager.storeTokenSecurely(secureToken);
            } else {
                const simpleToken = 'token_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                sessionStorage.setItem('secure_token', simpleToken);
            }
            
            // Armazenar dados do usuário (não sensíveis)
            const userDataSafe = { ...this.currentUser };
            delete userDataSafe.senha;
            localStorage.setItem('user_data', JSON.stringify(userDataSafe));

            this.showAlert('Conta criada com sucesso! (modo local)', 'success');
            
            setTimeout(() => {
                this.showCompanySelection();
            }, 1500);

        } catch (error) {
            console.error('❌ Erro no handleRegister:', error);
            this.showAlert('Erro ao criar conta: ' + error.message, 'danger');
        } finally {
            this.showLoading(false);
        }
        } catch (error) {
            console.error('❌ Erro geral no handleRegister:', error);
            this.showAlert('Erro inesperado: ' + error.message, 'danger');
        }
    }

    async handleLogin() {
        const email = document.getElementById('loginEmail').value.trim().toLowerCase();
        const senha = document.getElementById('loginSenha').value;

        if (!email || !senha) {
            this.showAlert('Preencha todos os campos', 'warning');
            return;
        }

        try {
            // MODO TESTE: Verificação de tentativas de login desabilitada
            // if (typeof securityManager !== 'undefined' && securityManager.checkLoginAttempts) {
            //     securityManager.checkLoginAttempts(email);
            // }
            
            this.showLoading(true);
            
            // Validar credenciais
            const loginResult = await this.validateUserCredentials(email, senha);
            
            if (!loginResult.success) {
                this.showAlert(loginResult.message, 'danger');
                
                // MODO TESTE: Registro de tentativas falhadas desabilitado
                // if (typeof securityManager !== 'undefined' && securityManager.recordLoginAttempt) {
                //     securityManager.recordLoginAttempt(email, false);
                // }
                return;
            }
            
            // Login válido
            this.currentUser = loginResult.user;

            // Gerar token seguro
            if (typeof securityManager !== 'undefined' && securityManager.generateSecureToken) {
                const secureToken = securityManager.generateSecureToken();
                securityManager.storeTokenSecurely(secureToken);
            } else {
                // Fallback simples
                console.log('⚠️ SecurityManager não disponível, usando token simples');
                const simpleToken = 'token_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                sessionStorage.setItem('secure_token', simpleToken);
            }
            
            // Armazenar dados do usuário (não sensíveis)
            const userDataSafe = { ...this.currentUser };
            localStorage.setItem('user_data', JSON.stringify(userDataSafe));
            
            // Registrar login bem-sucedido
            if (typeof securityManager !== 'undefined' && securityManager.recordLoginAttempt) {
                securityManager.recordLoginAttempt(email, true);
            }

            this.showAlert('Login realizado com sucesso!', 'success');
            
            // Ir para seleção de empresa
            setTimeout(() => {
                this.showCompanySelection();
            }, 1500);

        } catch (error) {
            // Registrar tentativa falhada
            if (typeof securityManager !== 'undefined' && securityManager.recordLoginAttempt) {
                securityManager.recordLoginAttempt(email, false);
            }
            
            if (error.message.includes('bloqueada')) {
                this.showAlert(error.message, 'danger');
            } else {
                this.showAlert('Email ou senha incorretos', 'danger');
            }
        } finally {
            this.showLoading(false);
        }
    }

    showWelcome() {
        this.hideAllScreens();
        document.getElementById('welcomeScreen').classList.remove('d-none');
    }

    showRegister() {
        this.hideAllScreens();
        document.getElementById('registerScreen').classList.remove('d-none');
        
        // Focar no primeiro campo
        setTimeout(() => {
            document.getElementById('registerNome').focus();
        }, 100);
    }

    showLogin() {
        this.hideAllScreens();
        document.getElementById('loginScreen').classList.remove('d-none');
        
        // Focar no email
        setTimeout(() => {
            document.getElementById('loginEmail').focus();
        }, 100);
    }

    showCompanySelection() {
        this.hideAllScreens();
        document.getElementById('companySelectionScreen').classList.remove('d-none');
        
        // Carregar empresas do usuário
        this.loadUserCompanies();
    }

    showDashboard() {
        this.hideAllScreens();
        document.getElementById('dashboardScreen').classList.remove('d-none');
        
        // Atualizar interface com dados do usuário
        if (this.currentUser) {
            const userName = document.getElementById('userName');
            if (userName) {
                userName.textContent = `${this.currentUser.nome} ${this.currentUser.sobrenome}`;
            }
        }

        if (this.currentCompany) {
            const companyName = document.getElementById('currentCompanyName');
            if (companyName) {
                companyName.textContent = this.currentCompany.nome;
            }
        }
    }

    hideAllScreens() {
        const screens = [
            'welcomeScreen',
            'registerScreen', 
            'loginScreen',
            'companySelectionScreen',
            'dashboardScreen',
            'createCompanyScreen',
            'inviteUserScreen',
            'applicationsScreen',
            'createApplicationScreen'
        ];
        
        screens.forEach(screenId => {
            document.getElementById(screenId).classList.add('d-none');
        });
    }

    async loadUserCompanies() {
        const container = document.getElementById('userCompanies');
        
        try {
            // Buscar empresas vinculadas ao usuário logado
            const companies = await this.getUserCompaniesFromDB();
            
            console.log('🏢 Empresas encontradas para o usuário:', companies);

            if (companies.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-muted mb-4">
                        <i class="bi bi-building" style="font-size: 3rem;"></i>
                        <p class="mt-3">Você ainda não está vinculado a nenhuma empresa</p>
                    </div>
                `;
                return;
            }

            const html = companies.map(company => `
                <div class="company-item" onclick="selectCompany('${company.id}', '${company.nome}')">
                    <div class="company-info">
                        <h6>${company.nome}</h6>
                        <small class="text-muted">
                            CNPJ: ${company.cnpj} | 
                            Perfil: ${company.perfil === 'admin' ? 'Administrador' : 'Usuário'}
                        </small>
                    </div>
                    <div>
                        <i class="bi bi-arrow-right text-primary"></i>
                    </div>
                </div>
            `).join('');

            container.innerHTML = `
                <div class="mb-3">
                    <h5>Suas Empresas</h5>
                    <p class="text-muted small">Selecione uma empresa para continuar</p>
                </div>
                ${html}
            `;

        } catch (error) {
            container.innerHTML = `
                <div class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    <p>Erro ao carregar empresas</p>
                </div>
            `;
        }
    }

    async getUserCompaniesFromDB() {
        if (!this.currentUser || !this.currentUser.email) {
            console.warn('⚠️ Usuário não logado');
            return [];
        }

        try {
            // Tentar usar backend real primeiro
            if (this.backend) {
                console.log('🏢 Buscando empresas do usuário no backend...');
                const response = await this.backend.getUserCompanies(this.currentUser.id);
                
                if (response.success && response.companies) {
                    console.log(`📊 Backend retornou ${response.companies.length} empresa(s)`);
                    return response.companies;
                }
            }
        } catch (error) {
            console.warn('⚠️ Erro ao buscar empresas no backend, usando fallback:', error.message);
        }

        // Fallback para dados simulados
        console.log('🔄 Usando dados simulados de empresas...');
        const userCompanyData = {
            'joao.silva@teste.com': [
                {
                    id: '73db40c3-9919-439b-bf5f-cb018770b8ca',
                    nome: 'UPTAX SOLUCOES TRIBUTARIAS DIGITAIS',
                    cnpj: '46.845.239/0001-63',
                    perfil: 'admin',
                    tipo: 'associada'
                }
            ],
            'kleber.ribeiro@uptax.net': [
                {
                    id: '73db40c3-9919-439b-bf5f-cb018770b8ca',
                    nome: 'UPTAX SOLUCOES TRIBUTARIAS DIGITAIS',
                    cnpj: '46.845.239/0001-63',
                    perfil: 'admin',
                    tipo: 'associada'
                },
                {
                    id: 'a1b2c3d4-5678-9abc-def0-123456789abc',
                    nome: 'NEXT CONTABILIDADE LTDA',
                    cnpj: '12.345.678/0001-90',
                    perfil: 'admin',
                    tipo: 'criada'
                }
            ],
            'admin@uptax.net': [
                {
                    id: '73db40c3-9919-439b-bf5f-cb018770b8ca',
                    nome: 'UPTAX SOLUCOES TRIBUTARIAS DIGITAIS',
                    cnpj: '46.845.239/0001-63',
                    perfil: 'super-admin',
                    tipo: 'administrador'
                },
                {
                    id: 'a1b2c3d4-5678-9abc-def0-123456789abc',
                    nome: 'NEXT CONTABILIDADE LTDA',
                    cnpj: '12.345.678/0001-90',
                    perfil: 'super-admin',
                    tipo: 'administrador'
                }
            ]
        };

        const userEmail = this.currentUser.email.toLowerCase();
        const userCompanies = userCompanyData[userEmail] || [];
        
        console.log(`📊 Fallback: Usuário ${userEmail} tem ${userCompanies.length} empresa(s)`);
        
        return userCompanies;
    }

    getCompaniesCreatedByUser(userEmail) {
        // Simular busca de empresas criadas pelo usuário
        // Isso representaria uma query SQL real: 
        // SELECT * FROM empresa WHERE criado_por = 'userEmail'
        
        // Por enquanto, assumindo que não há campo 'criado_por' na tabela
        // Esta seria a implementação futura quando o campo for adicionado
        
        const companiesCreatedByUser = {
            'joao.silva@teste.com': [
                // Adicione aqui empresas que foram criadas por este usuário
                // Exemplo: se o usuário criou uma nova empresa ontem
            ]
        };

        return companiesCreatedByUser[userEmail] || [];
    }

    async validateUserCredentials(email, senha) {
        try {
            // Tentar usar backend real primeiro
            if (this.backend) {
                console.log('🔐 Validando credenciais no backend...');
                const response = await this.backend.login(email, senha);
                
                if (response.success) {
                    return {
                        success: true,
                        user: response.user,
                        token: response.token
                    };
                } else {
                    return {
                        success: false,
                        message: response.message || 'Credenciais inválidas'
                    };
                }
            }
        } catch (error) {
            console.warn('⚠️ Erro no backend, usando fallback:', error.message);
        }

        // Fallback para dados simulados se backend falhar
        console.log('🔄 Usando validação de fallback...');
        await new Promise(resolve => setTimeout(resolve, 800));
        
        const validUsers = {
            'joao.silva@teste.com': {
                senha: '123456',
                user: {
                    id: 'user-joao-silva',
                    nome: 'João',
                    sobrenome: 'Silva',
                    email: 'joao.silva@teste.com',
                    telefone: '(11) 99999-9999'
                }
            },
            'kleber.ribeiro@uptax.net': {
                senha: 'senha123',
                user: {
                    id: 'user-kleber-ribeiro',
                    nome: 'Kleber',
                    sobrenome: 'Ribeiro',
                    email: 'kleber.ribeiro@uptax.net',
                    telefone: '(11) 98888-8888'
                }
            },
            'admin@uptax.net': {
                senha: 'admin123',
                user: {
                    id: 'user-admin',
                    nome: 'Admin',
                    sobrenome: 'Uptax',
                    email: 'admin@uptax.net',
                    telefone: '(11) 97777-7777'
                }
            }
        };

        const userRecord = validUsers[email.toLowerCase()];
        
        if (!userRecord) {
            return {
                success: false,
                message: 'Email não encontrado. Verifique ou cadastre-se.'
            };
        }

        if (userRecord.senha !== senha) {
            return {
                success: false,
                message: 'Senha incorreta. Tente novamente.'
            };
        }

        return {
            success: true,
            user: userRecord.user
        };
    }

    selectCompany(companyId, companyName) {
        this.currentCompany = {
            id: companyId,
            nome: companyName
        };

        localStorage.setItem('current_company', JSON.stringify(this.currentCompany));
        
        this.showAlert(`Empresa "${companyName}" selecionada!`, 'success');
        
        setTimeout(() => {
            this.showDashboard();
        }, 1000);
    }

    logout() {
        if (confirm('Tem certeza que deseja sair?')) {
            // Usar método seguro do SecurityManager
            if (typeof securityManager !== 'undefined' && securityManager.clearSecureToken) {
                securityManager.clearSecureToken();
            } else {
                // Fallback manual
                console.log('⚠️ SecurityManager não disponível, limpando dados manualmente');
                sessionStorage.removeItem('secure_token');
                localStorage.removeItem('user_data');
                localStorage.removeItem('current_company');
            }
            
            this.currentUser = null;
            this.currentCompany = null;
            
            this.showAlert('Logout realizado com sucesso!', 'info');
            
            setTimeout(() => {
                this.showWelcome();
            }, 1000);
        }
    }

    // Adicionar método de validação de email
    validateEmail(email) {
        const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return pattern.test(email);
    }

    // Atualizar indicador de força da senha
    updatePasswordStrength(password) {
        const strengthContainer = document.querySelector('.password-strength');
        if (!strengthContainer) return;

        if (password.length === 0) {
            strengthContainer.classList.add('d-none');
            return;
        }

        strengthContainer.classList.remove('d-none');
        
        let score = 0;
        if (typeof securityManager !== 'undefined' && securityManager.validatePassword) {
            const validation = securityManager.validatePassword(password);
            score = validation.score;
        } else {
            // Cálculo básico de força da senha
            score = Math.min(password.length * 10, 100);
            if (/[a-z]/.test(password)) score += 10;
            if (/[A-Z]/.test(password)) score += 10;
            if (/[0-9]/.test(password)) score += 10;
            if (/[^A-Za-z0-9]/.test(password)) score += 10;
        }
        
        // Remover classes anteriores
        strengthContainer.classList.remove('strength-weak', 'strength-fair', 'strength-good', 'strength-strong');
        
        let strengthClass = 'strength-weak';
        let strengthText = 'Muito fraca';
        
        if (score >= 80) {
            strengthClass = 'strength-strong';
            strengthText = 'Muito forte';
        } else if (score >= 60) {
            strengthClass = 'strength-good';
            strengthText = 'Boa';
        } else if (score >= 40) {
            strengthClass = 'strength-fair';
            strengthText = 'Regular';
        }
        
        strengthContainer.classList.add(strengthClass);
        strengthContainer.querySelector('.strength-text').textContent = strengthText;
    }

    switchCompany() {
        this.showCompanySelection();
    }

    // Utilitários
    async simulateApiCall() {
        // Simular delay de API
        return new Promise(resolve => {
            setTimeout(resolve, 1000 + Math.random() * 1000);
        });
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.toggle('d-none', !show);
        }
    }

    showAlert(message, type = 'info') {
        // Remover alertas existentes
        const existingAlerts = document.querySelectorAll('.alert-floating');
        existingAlerts.forEach(alert => alert.remove());
        
        // Criar novo alerta
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
        
        // Auto-remove após 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // ===============================
    // FORMATAÇÃO DE TELEFONE
    // ===============================

    setupPhoneFormatting() {
        const phoneInput = document.getElementById('registerTelefone');
        const countrySelect = document.getElementById('countryCode');
        
        if (!phoneInput || !countrySelect) return;

        console.log('📱 Configurando formatação de telefone...');

        // Formatar telefone quando o usuário digitar
        phoneInput.addEventListener('input', (e) => {
            const country = countrySelect.value;
            const formattedValue = this.formatPhoneNumber(e.target.value, country);
            e.target.value = formattedValue;
        });

        // Reformatar quando trocar de país
        countrySelect.addEventListener('change', (e) => {
            const country = e.target.value;
            const currentValue = phoneInput.value;
            if (currentValue) {
                const cleanValue = this.cleanPhoneNumber(currentValue);
                phoneInput.value = this.formatPhoneNumber(cleanValue, country);
            }
            
            // Atualizar placeholder
            this.updatePhonePlaceholder(country);
        });

        // Configurar placeholder inicial
        this.updatePhonePlaceholder(countrySelect.value);
    }

    formatPhoneNumber(value, countryCode) {
        // Limpar o número primeiro
        const cleanValue = this.cleanPhoneNumber(value);
        
        switch (countryCode) {
            case '+55': // Brasil
                return this.formatBrazilPhone(cleanValue);
            case '+1': // EUA/Canadá
                return this.formatUSPhone(cleanValue);
            case '+44': // Reino Unido
                return this.formatUKPhone(cleanValue);
            case '+33': // França
                return this.formatFrancePhone(cleanValue);
            case '+49': // Alemanha
                return this.formatGermanyPhone(cleanValue);
            default:
                return this.formatGenericPhone(cleanValue);
        }
    }

    cleanPhoneNumber(value) {
        return value.replace(/\D/g, '');
    }

    formatBrazilPhone(value) {
        if (value.length <= 2) return value;
        if (value.length <= 7) return `(${value.slice(0, 2)}) ${value.slice(2)}`;
        if (value.length <= 11) {
            const part1 = value.slice(0, 2);
            const part2 = value.slice(2, 7);
            const part3 = value.slice(7);
            return `(${part1}) ${part2}-${part3}`;
        }
        // Para números com 11 dígitos (celular)
        const part1 = value.slice(0, 2);
        const part2 = value.slice(2, 7);
        const part3 = value.slice(7, 11);
        return `(${part1}) ${part2}-${part3}`;
    }

    formatUSPhone(value) {
        if (value.length <= 3) return value;
        if (value.length <= 6) return `(${value.slice(0, 3)}) ${value.slice(3)}`;
        return `(${value.slice(0, 3)}) ${value.slice(3, 6)}-${value.slice(6, 10)}`;
    }

    formatUKPhone(value) {
        if (value.length <= 4) return value;
        if (value.length <= 7) return `${value.slice(0, 4)} ${value.slice(4)}`;
        return `${value.slice(0, 4)} ${value.slice(4, 7)} ${value.slice(7, 11)}`;
    }

    formatFrancePhone(value) {
        if (value.length <= 2) return value;
        const formatted = value.match(/.{1,2}/g)?.join(' ') || value;
        return formatted.slice(0, 14); // Limite de 10 dígitos
    }

    formatGermanyPhone(value) {
        if (value.length <= 3) return value;
        if (value.length <= 6) return `${value.slice(0, 3)} ${value.slice(3)}`;
        return `${value.slice(0, 3)} ${value.slice(3, 6)} ${value.slice(6, 10)}`;
    }

    formatGenericPhone(value) {
        // Formato genérico: grupos de 3-4 dígitos
        if (value.length <= 4) return value;
        if (value.length <= 8) return `${value.slice(0, 4)} ${value.slice(4)}`;
        return `${value.slice(0, 4)} ${value.slice(4, 8)} ${value.slice(8, 12)}`;
    }

    updatePhonePlaceholder(countryCode) {
        const phoneInput = document.getElementById('registerTelefone');
        if (!phoneInput) return;

        const placeholders = {
            '+55': '(11) 99999-9999',
            '+1': '(555) 123-4567',
            '+44': '7700 900123',
            '+33': '06 12 34 56 78',
            '+49': '030 123 456',
            '+34': '600 123 456',
            '+39': '320 123 4567',
            '+52': '55 1234 5678',
            '+54': '11 1234 5678',
            '+56': '9 1234 5678'
        };

        phoneInput.placeholder = placeholders[countryCode] || 'Número do telefone';
    }
}

// Função global para toggle de senha
function togglePasswordVisibility(inputId, button) {
    const input = document.getElementById(inputId);
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
        button.setAttribute('title', 'Ocultar senha');
    } else {
        input.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
        button.setAttribute('title', 'Mostrar senha');
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    try {
        authManager = new AuthManager();
        window.authManager = authManager; // Disponibilizar globalmente
        console.log('✅ AuthManager inicializado com sucesso');
    } catch (error) {
        console.error('❌ Erro ao inicializar AuthManager:', error);
    }
});

// Fallback: tentar inicializar imediatamente se DOM já estiver pronto
if (document.readyState === 'loading') {
    // DOM ainda carregando, aguardar DOMContentLoaded
} else {
    // DOM já carregado, inicializar imediatamente
    try {
        authManager = new AuthManager();
        window.authManager = authManager;
        console.log('✅ AuthManager inicializado imediatamente');
    } catch (error) {
        console.error('❌ Erro ao inicializar AuthManager imediatamente:', error);
    }
}

// Função auxiliar para showAlert seguro
function safeShowAlert(message, type = 'info') {
    if (authManager && typeof authManager.showAlert === 'function') {
        authManager.showAlert(message, type);
    } else {
        // Fallback para alert nativo
        console.log(`[${type.toUpperCase()}] ${message}`);
        alert(message);
    }
}

// Funções globais para compatibilidade com HTML
function showWelcome() {
    if (authManager && authManager.showWelcome) {
        authManager.showWelcome();
    } else {
        console.warn('⚠️ authManager não inicializado ainda');
    }
}

function showRegister() {
    console.log('🔧 showRegister() chamada');
    try {
        // Tentar usar AuthManager se disponível
        if (authManager && typeof authManager.showRegister === 'function') {
            console.log('✅ Usando authManager.showRegister()');
            authManager.showRegister();
            return;
        }
        
        // Fallback manual se AuthManager não estiver pronto
        console.log('🔄 Usando fallback manual para showRegister()');
        hideAllScreens();
        const registerScreen = document.getElementById('registerScreen');
        if (registerScreen) {
            registerScreen.classList.remove('d-none');
            console.log('✅ Tela de registro exibida (fallback)');
        } else {
            console.error('❌ Elemento registerScreen não encontrado');
        }
    } catch (error) {
        console.error('❌ Erro em showRegister():', error);
    }
}

function showLogin() {
    console.log('🔧 showLogin() chamada');
    try {
        // Tentar usar AuthManager se disponível
        if (authManager && typeof authManager.showLogin === 'function') {
            console.log('✅ Usando authManager.showLogin()');
            authManager.showLogin();
            return;
        }
        
        // Fallback manual se AuthManager não estiver pronto
        console.log('🔄 Usando fallback manual para showLogin()');
        hideAllScreens();
        const loginScreen = document.getElementById('loginScreen');
        if (loginScreen) {
            loginScreen.classList.remove('d-none');
            console.log('✅ Tela de login exibida (fallback)');
        } else {
            console.error('❌ Elemento loginScreen não encontrado');
        }
    } catch (error) {
        console.error('❌ Erro em showLogin():', error);
    }
}

// Função auxiliar para fallback
function hideAllScreens() {
    const screens = [
        'welcomeScreen',
        'registerScreen', 
        'loginScreen',
        'companySelectionScreen',
        'dashboardScreen',
        'createCompanyScreen',
        'inviteUserScreen',
        'applicationsScreen',
        'createApplicationScreen',
        'companyApplicationsScreen',
        'configureAppCredentialsScreen'
    ];
    
    screens.forEach(screenId => {
        const screen = document.getElementById(screenId);
        if (screen) {
            screen.classList.add('d-none');
        }
    });
}

function selectCompany(id, name) {
    if (authManager && authManager.selectCompany) {
        authManager.selectCompany(id, name);
    } else {
        console.warn('⚠️ authManager não inicializado ainda');
    }
}

function logout() {
    if (authManager && authManager.logout) {
        authManager.logout();
    } else {
        console.warn('⚠️ authManager não inicializado ainda');
    }
}

function switchCompany() {
    if (authManager && authManager.switchCompany) {
        authManager.switchCompany();
    } else {
        console.warn('⚠️ authManager não inicializado ainda');
    }
}

function showCreateCompany() {
    hideAllScreens();
    document.getElementById('createCompanyScreen').classList.remove('d-none');
    
    // Limpar formulário antes de configurar
    clearCompanyForm();
    setupCompanyForm();
    
    // Scroll para o topo
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showJoinCompany() {
    safeShowAlert('Funcionalidade de juntar-se à empresa em desenvolvimento', 'info');
}

// ===============================
// FUNCIONALIDADES DO DASHBOARD
// ===============================

function generateNewMCPKey() {
    // Simular geração de nova chave MCP
    const keyName = prompt('Nome para a nova chave MCP:');
    if (keyName) {
        safeShowAlert(`Chave MCP "${keyName}" criada com sucesso!`, 'success');
        // TODO: Implementar criação real da chave
        setTimeout(() => {
            refreshMCPKeys();
        }, 1000);
    }
}

function copyMCPKey(keyId) {
    // Simular cópia da chave
    const fakeKey = `mcp_${keyId}_${Date.now()}_abcd1234`;
    
    // Tentar usar a API moderna de clipboard
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(fakeKey).then(() => {
            safeShowAlert('Chave MCP copiada para a área de transferência!', 'success');
        }).catch(() => {
            // Fallback se a API moderna falhar
            copyToClipboardFallback(fakeKey);
        });
    } else {
        // Fallback para navegadores mais antigos
        copyToClipboardFallback(fakeKey);
    }
}

function copyToClipboardFallback(text) {
    // Criar elemento temporário
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        safeShowAlert('Chave MCP copiada para a área de transferência!', 'success');
    } catch (err) {
        safeShowAlert('Não foi possível copiar a chave. Copie manualmente: ' + text, 'warning');
    }
    
    document.body.removeChild(textArea);
}

function revokeMCPKey(keyId) {
    if (confirm('Tem certeza que deseja revogar esta chave MCP? Esta ação não pode ser desfeita.')) {
        safeShowAlert('Chave MCP revogada com sucesso!', 'success');
        // TODO: Implementar revogação real da chave
        setTimeout(() => {
            refreshMCPKeys();
        }, 1000);
    }
}

function refreshMCPKeys() {
    safeShowAlert('Atualizando lista de chaves MCP...', 'info');
    // TODO: Implementar atualização real das chaves
}

function showInviteUser() {
    hideAllScreens();
    document.getElementById('inviteUserScreen').classList.remove('d-none');
    setupInviteForm();
}

function showUserProfile() {
    safeShowAlert('Página de perfil em desenvolvimento', 'info');
    // TODO: Implementar página de perfil
}

function showAccountSettings() {
    safeShowAlert('Página de configurações em desenvolvimento', 'info');
    // TODO: Implementar página de configurações
}

function showAPIDocumentation() {
    safeShowAlert('Documentação da API em desenvolvimento', 'info');
    // TODO: Implementar documentação da API
}

// Função temporária para acessar aplicações (pode ser chamada do console)
function openApplications() {
    showApplications();
}

function showUsageStats() {
    safeShowAlert('Estatísticas de uso em desenvolvimento', 'info');
    // TODO: Implementar estatísticas
}

function showAllTeamMembers() {
    safeShowAlert('Lista completa da equipe em desenvolvimento', 'info');
    // TODO: Implementar lista completa da equipe
}

// ===============================
// CRIAÇÃO DE EMPRESA
// ===============================

function clearCompanyForm() {
    console.log('🧹 Limpando formulário de criação de empresa...');
    
    // Lista de todos os campos do formulário de empresa
    const fieldIds = [
        'companyName', 'companyCNPJ', 'companyEmail', 'companyPhone',
        'companyCEP', 'companyLogradouro', 'companyNumero', 'companyComplemento',
        'companyBairro', 'companyCidade', 'companyEstado', 'companyPais'
    ];
    
    // Limpar valores dos campos
    fieldIds.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = '';
            // Remover classes de validação
            field.classList.remove('is-valid', 'is-invalid');
        }
    });
    
    // Resetar selects para valores padrão
    const phoneCountrySelect = document.getElementById('companyPhoneCountry');
    if (phoneCountrySelect) {
        phoneCountrySelect.value = '+55'; // Brasil como padrão
    }
    
    const countrySelect = document.getElementById('companyPais');
    if (countrySelect) {
        countrySelect.value = 'Brasil'; // Brasil como padrão
    }
    
    const stateSelect = document.getElementById('companyEstado');
    if (stateSelect) {
        stateSelect.value = ''; // Limpar seleção de estado
    }
    
    // Limpar mensagens de status
    const statusElements = ['cnpjStatus', 'cepStatus', 'companyEmailStatus'];
    statusElements.forEach(statusId => {
        const statusElement = document.getElementById(statusId);
        if (statusElement) {
            statusElement.innerHTML = '<span class="text-muted">Digite para validar</span>';
        }
    });
    
    // Focar no primeiro campo
    setTimeout(() => {
        const firstField = document.getElementById('companyName');
        if (firstField) {
            firstField.focus();
        }
    }, 100);
    
    console.log('✅ Formulário de empresa limpo com sucesso');
}

function setupCompanyForm() {
    console.log('📋 Configurando formulário de criação de empresa...');
    
    // Configurar formatação de CNPJ
    const cnpjInput = document.getElementById('companyCNPJ');
    if (cnpjInput) {
        cnpjInput.addEventListener('input', formatCNPJInput);
        cnpjInput.addEventListener('blur', validateCNPJ);
    }
    
    // Configurar busca de CEP
    const cepInput = document.getElementById('companyCEP');
    if (cepInput) {
        cepInput.addEventListener('input', formatCEPInput);
        cepInput.addEventListener('blur', lookupCEP);
    }
    
    // Configurar formatação de telefone da empresa
    const companyPhoneInput = document.getElementById('companyPhone');
    const companyCountrySelect = document.getElementById('companyPhoneCountry');
    
    if (companyPhoneInput && companyCountrySelect) {
        companyPhoneInput.addEventListener('input', (e) => {
            const country = companyCountrySelect.value;
            const formattedValue = formatPhoneNumber(e.target.value, country);
            e.target.value = formattedValue;
        });
        
        companyCountrySelect.addEventListener('change', (e) => {
            const country = e.target.value;
            const currentValue = companyPhoneInput.value;
            if (currentValue) {
                const cleanValue = cleanPhoneNumber(currentValue);
                companyPhoneInput.value = formatPhoneNumber(cleanValue, country);
            }
            updateCompanyPhonePlaceholder(country);
        });
        
        updateCompanyPhonePlaceholder(companyCountrySelect.value);
    }
    
    // Configurar formulário de submissão
    const createCompanyForm = document.getElementById('createCompanyForm');
    if (createCompanyForm) {
        createCompanyForm.addEventListener('submit', handleCreateCompany);
    }
}

function formatCNPJInput(e) {
    let value = e.target.value.replace(/\D/g, '');
    
    if (value.length <= 14) {
        value = value.replace(/^(\d{2})(\d)/, '$1.$2');
        value = value.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
        value = value.replace(/\.(\d{3})(\d)/, '.$1/$2');
        value = value.replace(/(\d{4})(\d)/, '$1-$2');
    }
    
    e.target.value = value;
}

function validateCNPJ() {
    const cnpjInput = document.getElementById('companyCNPJ');
    const cnpjStatus = document.getElementById('cnpjStatus');
    
    if (!cnpjInput || !cnpjStatus) return;
    
    const cnpj = cnpjInput.value.replace(/\D/g, '');
    
    if (cnpj.length === 0) {
        cnpjStatus.textContent = 'CNPJ é obrigatório';
        cnpjStatus.className = 'text-danger';
        cnpjInput.setCustomValidity('CNPJ é obrigatório');
        return;
    }
    
    if (cnpj.length !== 14) {
        cnpjStatus.textContent = 'CNPJ deve ter 14 dígitos';
        cnpjStatus.className = 'text-danger';
        cnpjInput.setCustomValidity('CNPJ deve ter 14 dígitos');
        return;
    }
    
    if (isValidCNPJ(cnpj)) {
        cnpjStatus.innerHTML = '<i class="bi bi-check-circle me-1"></i>CNPJ válido';
        cnpjStatus.className = 'text-success';
        cnpjInput.setCustomValidity('');
    } else {
        cnpjStatus.innerHTML = '<i class="bi bi-x-circle me-1"></i>CNPJ inválido';
        cnpjStatus.className = 'text-danger';
        cnpjInput.setCustomValidity('CNPJ inválido');
    }
}

function isValidCNPJ(cnpj) {
    if (cnpj.length !== 14) return false;
    
    // Eliminar CNPJs conhecidos como inválidos
    if (/^(\d)\1{13}$/.test(cnpj)) return false;
    
    // Validar primeiro dígito verificador
    let soma = 0;
    let peso = 2;
    
    for (let i = 11; i >= 0; i--) {
        soma += parseInt(cnpj.charAt(i)) * peso;
        peso = peso === 9 ? 2 : peso + 1;
    }
    
    let resto = soma % 11;
    let digito1 = resto < 2 ? 0 : 11 - resto;
    
    if (parseInt(cnpj.charAt(12)) !== digito1) return false;
    
    // Validar segundo dígito verificador
    soma = 0;
    peso = 2;
    
    for (let i = 12; i >= 0; i--) {
        soma += parseInt(cnpj.charAt(i)) * peso;
        peso = peso === 9 ? 2 : peso + 1;
    }
    
    resto = soma % 11;
    let digito2 = resto < 2 ? 0 : 11 - resto;
    
    return parseInt(cnpj.charAt(13)) === digito2;
}

function formatCEPInput(e) {
    let value = e.target.value.replace(/\D/g, '');
    
    if (value.length <= 8) {
        value = value.replace(/^(\d{5})(\d)/, '$1-$2');
    }
    
    e.target.value = value;
}

async function lookupCEP() {
    const cepInput = document.getElementById('companyCEP');
    const cepStatus = document.getElementById('cepStatus');
    
    if (!cepInput || !cepStatus) return;
    
    const cep = cepInput.value.replace(/\D/g, '');
    
    if (cep.length !== 8) {
        cepStatus.textContent = 'CEP deve ter 8 dígitos';
        cepStatus.className = 'text-danger';
        return;
    }
    
    try {
        cepStatus.innerHTML = '<i class="bi bi-search me-1"></i>Buscando CEP...';
        cepStatus.className = 'text-primary';
        
        const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
        const data = await response.json();
        
        if (data.erro) {
            cepStatus.innerHTML = '<i class="bi bi-x-circle me-1"></i>CEP não encontrado';
            cepStatus.className = 'text-danger';
            return;
        }
        
        // Preencher campos automaticamente
        document.getElementById('companyLogradouro').value = data.logradouro || '';
        document.getElementById('companyBairro').value = data.bairro || '';
        document.getElementById('companyCidade').value = data.localidade || '';
        document.getElementById('companyEstado').value = data.uf || '';
        
        cepStatus.innerHTML = '<i class="bi bi-check-circle me-1"></i>CEP encontrado e endereço preenchido';
        cepStatus.className = 'text-success';
        
        // Focar no próximo campo (número)
        setTimeout(() => {
            document.getElementById('companyNumero').focus();
        }, 100);
        
    } catch (error) {
        console.error('Erro ao buscar CEP:', error);
        cepStatus.innerHTML = '<i class="bi bi-exclamation-triangle me-1"></i>Erro ao buscar CEP';
        cepStatus.className = 'text-warning';
    }
}

function updateCompanyPhonePlaceholder(countryCode) {
    const phoneInput = document.getElementById('companyPhone');
    if (!phoneInput) return;
    
    const placeholders = {
        '+55': '(11) 3333-4444',
        '+1': '(555) 123-4567',
        '+44': '20 7123 4567',
        '+33': '01 23 45 67 89',
        '+49': '030 123 456',
        '+34': '91 123 45 67',
        '+39': '06 1234 5678',
        '+52': '55 1234 5678',
        '+54': '11 1234 5678',
        '+56': '2 1234 5678'
    };
    
    phoneInput.placeholder = placeholders[countryCode] || 'Telefone da empresa';
}

function formatPhoneNumber(value, countryCode) {
    if (!authManager || typeof authManager.formatPhoneNumber !== 'function') {
        // Fallback básico
        const cleanValue = value.replace(/\D/g, '');
        if (countryCode === '+55') {
            // Formato brasileiro
            if (cleanValue.length <= 2) return cleanValue;
            if (cleanValue.length <= 6) return `(${cleanValue.slice(0, 2)}) ${cleanValue.slice(2)}`;
            return `(${cleanValue.slice(0, 2)}) ${cleanValue.slice(2, 6)}-${cleanValue.slice(6, 10)}`;
        }
        return cleanValue;
    }
    
    return authManager.formatPhoneNumber(value, countryCode);
}

function cleanPhoneNumber(value) {
    return value.replace(/\D/g, '');
}

async function handleCreateCompany(e) {
    e.preventDefault();
    
    try {
        // Validar CNPJ antes de enviar
        const cnpjInput = document.getElementById('companyCNPJ');
        if (cnpjInput && cnpjInput.validity && !cnpjInput.validity.valid) {
            safeShowAlert('Corrija os erros no formulário antes de continuar', 'danger');
            cnpjInput.focus();
            return;
        }
        
        const formData = {
            nome: document.getElementById('companyName').value.trim(),
            cnpj: document.getElementById('companyCNPJ').value.replace(/\D/g, ''),
            email: document.getElementById('companyEmail').value.trim(),
            telefone: document.getElementById('companyPhone').value.trim(),
            cep: document.getElementById('companyCEP').value.replace(/\D/g, ''),
            logradouro: document.getElementById('companyLogradouro').value.trim(),
            numero: document.getElementById('companyNumero').value.trim(),
            complemento: document.getElementById('companyComplemento').value.trim(),
            bairro: document.getElementById('companyBairro').value.trim(),
            cidade: document.getElementById('companyCidade').value.trim(),
            estado: document.getElementById('companyEstado').value,
            pais: document.getElementById('companyPais').value
        };
        
        // Validações básicas
        if (!formData.nome || !formData.cnpj || !formData.email) {
            safeShowAlert('Preencha todos os campos obrigatórios', 'danger');
            return;
        }
        
        if (!authManager || typeof authManager.validateEmail !== 'function' || 
            !authManager.validateEmail(formData.email)) {
            safeShowAlert('E-mail inválido', 'danger');
            return;
        }

        // Validações de unicidade (se validationManager estiver disponível)
        if (typeof validationManager !== 'undefined') {
            const validation = await validationManager.validateFormBeforeSubmit(formData, 'company');
            if (!validation.valid) {
                safeShowAlert('Erro de validação:<br>' + validation.errors.join('<br>'), 'danger');
                return;
            }
        }
        
        // Combinar telefone com código do país
        const countryCode = document.getElementById('companyPhoneCountry').value;
        if (formData.telefone) {
            formData.telefone = `${countryCode} ${formData.telefone}`;
        }
        
        safeShowAlert('Criando empresa...', 'info');
        
        // Simular criação da empresa
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        safeShowAlert('Empresa criada com sucesso!', 'success');
        
        // Voltar para seleção de empresas após 2 segundos
        setTimeout(() => {
            if (authManager && authManager.showCompanySelection) {
                authManager.showCompanySelection();
            } else {
                hideAllScreens();
                document.getElementById('companySelectionScreen').classList.remove('d-none');
            }
        }, 2000);
        
    } catch (error) {
        console.error('Erro ao criar empresa:', error);
        safeShowAlert('Erro ao criar empresa: ' + error.message, 'danger');
    }
}

// ===============================
// CONVITE DE USUÁRIOS
// ===============================

function setupInviteForm() {
    console.log('📋 Configurando formulário de convite de usuários...');
    
    // Configurar interações dos cards de nível de acesso
    const accessCards = document.querySelectorAll('.access-level-card');
    accessCards.forEach(card => {
        card.addEventListener('click', (e) => {
            // Se clicou no card (não no radio button), marcar o radio
            if (e.target.type !== 'radio') {
                const radio = card.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                    updateAccessLevelCards();
                    updateResponsibilityVisibility(radio.value);
                }
            }
        });
    });
    
    // Configurar radio buttons
    const accessRadios = document.querySelectorAll('input[name="accessLevel"]');
    accessRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            updateAccessLevelCards();
            updateResponsibilityVisibility(radio.value);
        });
    });
    
    // Configurar checkboxes de responsabilidade
    const responsibilityChecks = document.querySelectorAll('input[name="responsibilities"]');
    responsibilityChecks.forEach(checkbox => {
        checkbox.addEventListener('change', updateInvitePreview);
    });
    
    // Configurar validação em tempo real
    const inviteForm = document.getElementById('inviteUserForm');
    const emailInput = document.getElementById('inviteEmail');
    
    if (emailInput) {
        emailInput.addEventListener('blur', validateInviteEmail);
        emailInput.addEventListener('input', validateInviteEmailRealTime);
    }
    
    if (inviteForm) {
        inviteForm.addEventListener('submit', handleSendInvite);
    }
    
    // Configurar outros campos para preview
    ['inviteNome', 'inviteSobrenome', 'inviteMessage'].forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', updateInvitePreview);
        }
    });
    
    // Foco inicial
    setTimeout(() => {
        const nomeInput = document.getElementById('inviteNome');
        if (nomeInput) nomeInput.focus();
    }, 100);
}

function updateAccessLevelCards() {
    const cards = document.querySelectorAll('.access-level-card');
    const selectedRadio = document.querySelector('input[name="accessLevel"]:checked');
    
    cards.forEach(card => {
        const radio = card.querySelector('input[type="radio"]');
        if (radio && radio.checked) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
}

function updateResponsibilityVisibility(accessLevel) {
    const responsibilitySection = document.querySelector('.responsibility-check').closest('.mb-3');
    
    if (!responsibilitySection) return;
    
    // Responsabilidades específicas são mais relevantes para membros e admins
    if (accessLevel === 'readonly') {
        responsibilitySection.style.opacity = '0.6';
        responsibilitySection.querySelector('label').textContent = 'Responsabilidades (limitadas para acesso somente leitura)';
    } else {
        responsibilitySection.style.opacity = '1';
        responsibilitySection.querySelector('label').textContent = 'Responsabilidades (opcional)';
    }
}

function validateInviteEmailRealTime() {
    const emailInput = document.getElementById('inviteEmail');
    if (!emailInput) return;
    
    const email = emailInput.value.trim();
    
    // Se estiver vazio, apenas limpar erro
    if (!email) {
        clearEmailError();
        return;
    }
    
    // Validação básica em tempo real
    if (!isValidEmail(email)) {
        setEmailError('E-mail inválido');
        return false;
    }
    
    // Verificar se e-mail já está cadastrado (simulação)
    const existingEmails = ['admin@empresa.com', 'user@test.com']; // Simular lista
    if (existingEmails.includes(email.toLowerCase())) {
        setEmailError('Este e-mail já está cadastrado na empresa');
        return false;
    }
    
    clearEmailError();
    return true;
}

function validateInviteEmail() {
    const emailInput = document.getElementById('inviteEmail');
    if (!emailInput) return false;
    
    const email = emailInput.value.trim();
    
    if (!email) {
        setEmailError('E-mail é obrigatório');
        return false;
    }
    
    if (!isValidEmail(email)) {
        setEmailError('E-mail inválido');
        return false;
    }
    
    // Verificar se e-mail já está cadastrado (simulação)
    const existingEmails = ['admin@empresa.com', 'user@test.com']; // Simular lista
    if (existingEmails.includes(email.toLowerCase())) {
        setEmailError('Este e-mail já está cadastrado na empresa');
        return false;
    }
    
    clearEmailError();
    return true;
}

function isValidEmail(email) {
    // Validação robusta de e-mail
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

function setEmailError(message) {
    const emailInput = document.getElementById('inviteEmail');
    const formText = emailInput.closest('.form-floating').querySelector('.form-text');
    
    emailInput.classList.add('is-invalid');
    if (formText) {
        formText.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-circle me-1"></i>${message}</span>`;
    }
}

function clearEmailError() {
    const emailInput = document.getElementById('inviteEmail');
    const formText = emailInput.closest('.form-floating').querySelector('.form-text');
    
    emailInput.classList.remove('is-invalid');
    if (formText) {
        formText.innerHTML = 'O convite será enviado para este e-mail';
    }
}

function updateInvitePreview() {
    // Esta função pode ser expandida para mostrar um preview do convite
    // Por enquanto, apenas logs para debug
    const nome = document.getElementById('inviteNome').value;
    const sobrenome = document.getElementById('inviteSobrenome').value;
    const email = document.getElementById('inviteEmail').value;
    const selectedAccess = document.querySelector('input[name="accessLevel"]:checked');
    const selectedResponsibilities = Array.from(document.querySelectorAll('input[name="responsibilities"]:checked'));
    
    console.log('Dados do convite:', {
        nome: nome + ' ' + sobrenome,
        email,
        accessLevel: selectedAccess?.value,
        responsibilities: selectedResponsibilities.map(r => r.value)
    });
}

async function handleSendInvite(e) {
    e.preventDefault();
    
    try {
        // Validações básicas
        const nome = document.getElementById('inviteNome').value.trim();
        const sobrenome = document.getElementById('inviteSobrenome').value.trim();
        const email = document.getElementById('inviteEmail').value.trim();
        const selectedAccess = document.querySelector('input[name="accessLevel"]:checked');
        
        if (!nome || !sobrenome || !email) {
            safeShowAlert('Preencha todos os campos obrigatórios', 'danger');
            return;
        }
        
        if (!selectedAccess) {
            safeShowAlert('Selecione um nível de acesso', 'danger');
            return;
        }
        
        if (!validateInviteEmail()) {
            return;
        }
        
        // Coletar responsabilidades selecionadas
        const selectedResponsibilities = Array.from(document.querySelectorAll('input[name="responsibilities"]:checked'))
            .map(checkbox => checkbox.value);
        
        const inviteData = {
            nome,
            sobrenome,
            email: email.toLowerCase(),
            accessLevel: selectedAccess.value,
            responsibilities: selectedResponsibilities,
            message: document.getElementById('inviteMessage').value.trim(),
            expirationHours: parseInt(document.getElementById('inviteExpiration').value),
            requirePasswordReset: document.getElementById('requirePasswordReset').checked,
            invitedBy: authManager?.currentUser?.email || 'admin@empresa.com',
            company: authManager?.currentCompany?.nome || 'Empresa Atual'
        };
        
        safeShowAlert('Enviando convite...', 'info');
        
        // Simular envio do convite
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Simular geração de link de convite
        const inviteToken = 'invite_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const inviteLink = `${window.location.origin}/accept-invite?token=${inviteToken}`;
        
        console.log('Convite enviado:', inviteData);
        console.log('Link do convite:', inviteLink);
        
        // Mostrar sucesso com detalhes
        const accessLevelText = {
            'admin': 'Administrador',
            'member': 'Membro',
            'readonly': 'Somente Leitura'
        };
        
        const responsibilityText = {
            'financeiro': 'Responsável Financeiro',
            'tecnico': 'Responsável Técnico', 
            'operacional': 'Responsável Operacional',
            'suporte': 'Suporte ao Cliente'
        };
        
        let successMessage = `Convite enviado para ${nome} ${sobrenome} (${email}) como ${accessLevelText[selectedAccess.value]}`;
        
        if (selectedResponsibilities.length > 0) {
            const responsibilities = selectedResponsibilities.map(r => responsibilityText[r]).join(', ');
            successMessage += ` com responsabilidades: ${responsibilities}`;
        }
        
        safeShowAlert(successMessage, 'success');
        
        // Voltar ao dashboard após 3 segundos
        setTimeout(() => {
            backToDashboard();
        }, 3000);
        
    } catch (error) {
        console.error('Erro ao enviar convite:', error);
        safeShowAlert('Erro ao enviar convite: ' + error.message, 'danger');
    }
}

function backToDashboard() {
    if (authManager && authManager.showDashboard) {
        authManager.showDashboard();
    } else {
        hideAllScreens();
        document.getElementById('dashboardScreen').classList.remove('d-none');
    }
}

// ===============================
// GERENCIAMENTO DE APLICAÇÕES
// ===============================

function showApplications() {
    hideAllScreens();
    document.getElementById('applicationsScreen').classList.remove('d-none');
    setupViewToggle();
    loadApplications();
}

function showCreateApplication() {
    hideAllScreens();
    document.getElementById('createApplicationScreen').classList.remove('d-none');
    setupApplicationForm();
    resetApplicationForm();
    
    // Limpar modo de edição
    delete window.editingAppId;
    
    // Restaurar título para "Configurar Nova Aplicação"
    document.getElementById('applicationFormTitle').textContent = 'Configurar Nova Aplicação';
}

function setupApplicationForm() {
    console.log('📋 Configurando formulário de aplicações...');
    
    // Configurar validação do ID da aplicação
    const appIdInput = document.getElementById('appId');
    if (appIdInput) {
        appIdInput.addEventListener('input', formatAppId);
        appIdInput.addEventListener('blur', validateAppId);
    }
    
    // Configurar formulário
    const applicationForm = document.getElementById('createApplicationForm');
    if (applicationForm) {
        applicationForm.addEventListener('submit', handleCreateApplication);
    }
    
    // Configurar geração automática de ID baseado no nome
    const appNameInput = document.getElementById('appName');
    if (appNameInput) {
        appNameInput.addEventListener('input', generateAppIdFromName);
    }
    
    console.log('✅ Formulário de aplicações configurado');
}

function formatAppId(e) {
    // Formatar ID: apenas letras minúsculas, números e hífens
    let value = e.target.value.toLowerCase();
    value = value.replace(/[^a-z0-9-]/g, '');
    value = value.replace(/--+/g, '-'); // Evitar hífens duplos
    value = value.replace(/^-|-$/g, ''); // Remover hífens no início/fim
    e.target.value = value;
}

function generateAppIdFromName() {
    const nameInput = document.getElementById('appName');
    const idInput = document.getElementById('appId');
    
    if (!nameInput || !idInput || idInput.value) return; // Não sobrescrever se já tem ID
    
    const name = nameInput.value.trim();
    if (!name) return;
    
    // Gerar ID automático baseado no nome
    let id = name.toLowerCase()
        .replace(/[^a-z0-9\s]/g, '') // Remover caracteres especiais
        .replace(/\s+/g, '-') // Substituir espaços por hífens
        .replace(/-+/g, '-') // Evitar hífens duplos
        .replace(/^-|-$/g, ''); // Remover hífens no início/fim
    
    idInput.value = id;
    validateAppId();
}

function validateAppId() {
    const appIdInput = document.getElementById('appId');
    if (!appIdInput) return;
    
    const id = appIdInput.value.trim();
    const existingIds = ['omie-mcp', 'claude-mcp', 'test-app']; // Simular IDs existentes
    
    if (!id) {
        setAppIdError('ID é obrigatório');
        return false;
    }
    
    if (id.length < 3) {
        setAppIdError('ID deve ter pelo menos 3 caracteres');
        return false;
    }
    
    if (existingIds.includes(id)) {
        setAppIdError('Este ID já está em uso');
        return false;
    }
    
    clearAppIdError();
    return true;
}

function setAppIdError(message) {
    const appIdInput = document.getElementById('appId');
    const formText = appIdInput.closest('.form-floating').querySelector('.form-text');
    
    appIdInput.classList.add('is-invalid');
    if (formText) {
        formText.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-circle me-1"></i>${message}</span>`;
    }
}

function clearAppIdError() {
    const appIdInput = document.getElementById('appId');
    const formText = appIdInput.closest('.form-floating').querySelector('.form-text');
    
    appIdInput.classList.remove('is-invalid');
    if (formText) {
        formText.innerHTML = 'Identificador único (ex: omie-mcp)';
    }
}

function addCustomCredential() {
    const container = document.getElementById('customCredentials');
    const index = container.children.length;
    
    const credentialHtml = `
        <div class="custom-credential-item mb-3" data-index="${index}">
            <div class="row">
                <div class="col-md-5">
                    <div class="form-floating">
                        <input type="text" class="form-control" id="customCredName_${index}" placeholder="Nome">
                        <label for="customCredName_${index}">Nome da Credencial</label>
                    </div>
                </div>
                <div class="col-md-5">
                    <div class="form-floating">
                        <select class="form-select" id="customCredType_${index}">
                            <option value="text">Texto</option>
                            <option value="password">Senha</option>
                            <option value="url">URL</option>
                            <option value="email">E-mail</option>
                            <option value="number">Número</option>
                        </select>
                        <label for="customCredType_${index}">Tipo</label>
                    </div>
                </div>
                <div class="col-md-2 d-flex align-items-center">
                    <button type="button" class="btn btn-outline-danger w-100" onclick="removeCustomCredential(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', credentialHtml);
}

function removeCustomCredential(index) {
    const item = document.querySelector(`[data-index="${index}"]`);
    if (item) {
        item.remove();
    }
}

function resetApplicationForm() {
    const form = document.getElementById('createApplicationForm');
    if (form) {
        form.reset();
        
        // Limpar credenciais customizadas
        const customCredentials = document.getElementById('customCredentials');
        if (customCredentials) {
            customCredentials.innerHTML = '';
        }
        
        // Limpar erros
        clearAppIdError();
        
        // Resetar título
        const title = document.getElementById('applicationFormTitle');
        if (title) {
            title.textContent = 'Nova Aplicação';
        }
    }
}

async function handleCreateApplication(e) {
    e.preventDefault();
    
    try {
        // Validações básicas
        const appName = document.getElementById('appName').value.trim();
        const appId = document.getElementById('appId').value.trim();
        const appDescription = document.getElementById('appDescription').value.trim();
        const appCategory = document.getElementById('appCategory').value;
        
        if (!appName || !appId || !appDescription || !appCategory) {
            safeShowAlert('Preencha todos os campos obrigatórios', 'danger');
            return;
        }
        
        if (!validateAppId()) {
            return;
        }
        
        // Coletar credenciais obrigatórias
        const requiredCredentials = Array.from(document.querySelectorAll('input[name="requiredCredentials"]:checked'))
            .map(checkbox => checkbox.value);
        
        // Coletar credenciais customizadas
        const customCredentials = [];
        const customCredItems = document.querySelectorAll('.custom-credential-item');
        customCredItems.forEach((item, index) => {
            const name = document.getElementById(`customCredName_${index}`)?.value.trim();
            const type = document.getElementById(`customCredType_${index}`)?.value;
            
            if (name && type) {
                customCredentials.push({ name, type, required: true });
            }
        });
        
        const applicationData = {
            id: appId,
            name: appName,
            description: appDescription,
            category: appCategory,
            status: document.getElementById('appStatus').value,
            url: document.getElementById('appUrl').value.trim(),
            authType: document.getElementById('authType').value,
            apiVersion: document.getElementById('apiVersion').value.trim(),
            notes: document.getElementById('appNotes').value.trim(),
            requiredCredentials: requiredCredentials,
            customCredentials: customCredentials,
            createdAt: new Date().toISOString(),
            createdBy: authManager?.currentUser?.email || 'admin@empresa.com'
        };
        
        safeShowAlert('Salvando aplicação...', 'info');
        
        // Simular salvamento
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        console.log('Aplicação criada:', applicationData);
        
        safeShowAlert(`Aplicação "${appName}" criada com sucesso!`, 'success');
        
        // Voltar para lista de aplicações
        setTimeout(() => {
            showApplications();
        }, 2000);
        
    } catch (error) {
        console.error('Erro ao criar aplicação:', error);
        safeShowAlert('Erro ao criar aplicação: ' + error.message, 'danger');
    }
}

let currentApplications = [];

function setupViewToggle() {
    const viewToggle = document.querySelectorAll('input[name="viewMode"]');
    viewToggle.forEach(radio => {
        radio.addEventListener('change', (e) => {
            switchView(e.target.value);
        });
    });
}

function switchView(viewMode) {
    // Ocultar todas as visualizações
    document.getElementById('applicationsGrid').classList.add('d-none');
    document.getElementById('applicationsList').classList.add('d-none');
    document.getElementById('applicationsTable').classList.add('d-none');
    
    // Mostrar visualização selecionada
    switch(viewMode) {
        case 'grid':
            document.getElementById('applicationsGrid').classList.remove('d-none');
            renderApplicationsGrid(currentApplications);
            break;
        case 'list':
            document.getElementById('applicationsList').classList.remove('d-none');
            renderApplicationsList(currentApplications);
            break;
        case 'table':
            document.getElementById('applicationsTable').classList.remove('d-none');
            renderApplicationsTable(currentApplications);
            break;
    }
}

function loadApplications() {
    console.log('📱 Carregando aplicações...');
    
    // Simular dados de aplicações
    currentApplications = [
        {
            id: 'omie-mcp',
            name: 'Omie MCP',
            description: 'Integração MCP para Omie ERP com funcionalidades completas de gestão',
            category: 'mcp',
            status: 'active',
            url: 'https://github.com/omie-mcp',
            authType: 'api_key',
            requiredCredentials: [
                { key: 'app_key', label: 'App Key', type: 'text', required: true, placeholder: 'Sua chave de aplicação Omie' },
                { key: 'app_secret', label: 'App Secret', type: 'password', required: true, placeholder: 'Seu secret da aplicação Omie' }
            ],
            customCredentials: [],
            createdAt: '2024-01-15T10:00:00Z'
        },
        {
            id: 'claude-mcp',
            name: 'Claude MCP Server',
            description: 'Servidor MCP para integração com Claude AI e automações inteligentes',
            category: 'ai',
            status: 'active',
            url: 'https://claude.ai/mcp',
            authType: 'bearer',
            requiredCredentials: [
                { key: 'token', label: 'API Token', type: 'password', required: true, placeholder: 'Token de acesso do Claude' },
                { key: 'api_url', label: 'API URL', type: 'url', required: true, placeholder: 'https://api.anthropic.com' }
            ],
            customCredentials: [
                { name: 'Model Version', type: 'text', required: false }
            ],
            createdAt: '2024-02-01T14:30:00Z'
        },
        {
            id: 'n8n-automation',
            name: 'N8N Automation',
            description: 'Plataforma de automação de fluxos de trabalho e integrações',
            category: 'automation',
            status: 'beta',
            url: 'https://n8n.io',
            authType: 'oauth2',
            requiredCredentials: [
                { key: 'email', label: 'Email', type: 'email', required: true, placeholder: 'seu@email.com' },
                { key: 'password', label: 'Senha', type: 'password', required: true, placeholder: 'Sua senha do N8N' },
                { key: 'api_url', label: 'URL da Instância', type: 'url', required: true, placeholder: 'https://sua-instancia.n8n.cloud' }
            ],
            customCredentials: [
                { name: 'Webhook URL', type: 'url', required: true }
            ],
            createdAt: '2024-01-20T16:45:00Z'
        },
        {
            id: 'financial-api',
            name: 'API Financeira',
            description: 'Integração com sistemas financeiros e bancários para automação',
            category: 'financial',
            status: 'inactive',
            url: 'https://financial-api.com',
            authType: 'api_key',
            requiredCredentials: [
                { key: 'app_key', label: 'App Key', type: 'text', required: true, placeholder: 'Chave da API financeira' },
                { key: 'app_secret', label: 'App Secret', type: 'password', required: true, placeholder: 'Secret da API financeira' },
                { key: 'api_url', label: 'URL da API', type: 'url', required: true, placeholder: 'https://api.financeira.com' }
            ],
            customCredentials: [],
            createdAt: '2024-01-10T09:15:00Z'
        }
    ];
    
    // Renderizar na visualização atual
    const selectedView = document.querySelector('input[name="viewMode"]:checked').value;
    switchView(selectedView);
}

function renderApplicationsGrid(applications) {
    const grid = document.getElementById('applicationsGrid');
    if (!grid) return;
    
    if (applications.length === 0) {
        grid.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-app-indicator" style="font-size: 3rem; color: var(--gray-400);"></i>
                <h5 class="mt-3 text-muted">Nenhuma aplicação encontrada</h5>
                <p class="text-muted">Crie a primeira aplicação para começar</p>
                <button class="btn btn-primary mt-2" onclick="showCreateApplication()">
                    <i class="bi bi-plus-circle me-2"></i>Nova Aplicação
                </button>
            </div>
        `;
        return;
    }
    
    const html = applications.map(app => `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card application-card h-100" data-app-id="${app.id}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div class="application-icon">
                            <i class="bi bi-${getCategoryIcon(app.category)} text-primary"></i>
                        </div>
                        <span class="badge bg-${getStatusColor(app.status)}">${getStatusText(app.status)}</span>
                    </div>
                    
                    <h5 class="card-title">${app.name}</h5>
                    <p class="card-text text-muted small">${app.description}</p>
                    
                    <div class="application-details mb-3">
                        <div class="row text-center">
                            <div class="col">
                                <small class="text-muted d-block">Tipo</small>
                                <strong class="small">${getCategoryText(app.category)}</strong>
                            </div>
                            <div class="col">
                                <small class="text-muted d-block">Credenciais</small>
                                <strong class="small">${app.requiredCredentials.length + (app.customCredentials ? app.customCredentials.length : 0)}</strong>
                            </div>
                        </div>
                    </div>
                    
                    <div class="application-credentials mb-3">
                        <small class="text-muted d-block mb-1">Credenciais necessárias:</small>
                        <div class="credential-tags">
                            ${app.requiredCredentials.map(cred => 
                                `<span class="badge bg-light text-dark me-1">${getCredentialText(cred)}</span>`
                            ).join('')}
                            ${app.customCredentials.map(cred => 
                                `<span class="badge bg-secondary me-1">${cred.name}</span>`
                            ).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="card-footer bg-transparent">
                    <div class="d-flex justify-content-between">
                        <button class="btn btn-outline-primary btn-sm" onclick="editApplication('${app.id}')">
                            <i class="bi bi-pencil me-1"></i>Editar
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="configureApplication('${app.id}')">
                            <i class="bi bi-gear me-1"></i>Configurar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    grid.innerHTML = html;
}

function getCategoryIcon(category) {
    const icons = {
        'erp': 'building',
        'mcp': 'plugin',
        'financial': 'currency-dollar',
        'automation': 'gear-wide-connected',
        'ai': 'brain',
        'integration': 'link-45deg'
    };
    return icons[category] || 'app-indicator';
}

function getStatusColor(status) {
    const colors = {
        'active': 'success',
        'beta': 'warning', 
        'inactive': 'secondary'
    };
    return colors[status] || 'secondary';
}

function getStatusText(status) {
    const texts = {
        'active': 'Ativo',
        'beta': 'Beta',
        'inactive': 'Inativo'
    };
    return texts[status] || status;
}

function getCategoryText(category) {
    const texts = {
        'erp': 'ERP',
        'mcp': 'MCP',
        'financial': 'Financeiro',
        'automation': 'Automação',
        'ai': 'IA',
        'integration': 'Integração'
    };
    return texts[category] || category;
}

function getCredentialText(credential) {
    // Se for objeto, usar label ou key
    if (typeof credential === 'object') {
        return credential.label || credential.key || 'Credencial';
    }
    
    // Se for string, usar mapeamento
    const texts = {
        'app_key': 'APP Key',
        'app_secret': 'APP Secret',
        'api_url': 'URL API',
        'email': 'E-mail',
        'password': 'Senha',
        'token': 'Token'
    };
    return texts[credential] || credential;
}

function filterApplications() {
    console.log('🔍 Filtrar aplicações...');
    // TODO: Implementar filtros
    const search = document.getElementById('searchApplications').value;
    const category = document.getElementById('filterCategory').value;
    const status = document.getElementById('filterStatus').value;
    
    console.log('Filtros:', { search, category, status });
    safeShowAlert('Filtros aplicados!', 'info');
}

function editApplication(appId) {
    console.log('✏️ Editar aplicação:', appId);
    
    // Encontrar a aplicação
    const app = mockApplications.find(a => a.id === appId);
    if (!app) {
        safeShowAlert('Aplicação não encontrada', 'danger');
        return;
    }
    
    // Ir para tela de criação com dados preenchidos
    hideAllScreens();
    document.getElementById('createApplicationScreen').classList.remove('d-none');
    
    // Preencher formulário com dados da aplicação
    fillApplicationForm(app);
    
    // Atualizar título para "Editar"
    const titleElement = document.getElementById('applicationFormTitle');
    if (titleElement) {
        titleElement.textContent = 'Editar Aplicação';
    }
    
    // Adicionar atributo para identificar que é edição
    const form = document.getElementById('applicationForm');
    if (form) {
        form.setAttribute('data-editing-app-id', appId);
    }
    
    safeShowAlert(`Editando aplicação: ${app.name}`, 'info');
}

function fillApplicationForm(app) {
    // Preencher campos básicos
    document.getElementById('appName').value = app.name || '';
    document.getElementById('appDescription').value = app.description || '';
    document.getElementById('appUrl').value = app.url || '';
    document.getElementById('authType').value = app.authType || 'api_key';
    document.getElementById('appNotes').value = app.notes || '';
    
    // Marcar tipo
    const categoryRadio = document.querySelector(`input[name="category"][value="${app.category}"]`);
    if (categoryRadio) {
        categoryRadio.checked = true;
    }
    
    // TODO: Preencher credenciais obrigatórias quando necessário
}

function configureApplication(appId) {
    console.log('⚙️ Configurar aplicação:', appId);
    
    // Encontrar a aplicação no catálogo
    const app = mockApplications.find(a => a.id === appId);
    if (!app) {
        safeShowAlert('Aplicação não encontrada', 'danger');
        return;
    }
    
    // Criar uma configuração temporária para a empresa atual
    const appConfig = {
        id: `config_${Date.now()}`,
        applicationId: app.id,
        applicationName: app.name,
        description: app.description,
        company: mockUserData.currentCompany,
        status: 'pending',
        credentials: {},
        requiredCredentials: app.requiredCredentials,
        createdAt: new Date().toISOString()
    };
    
    // Ir para tela de configuração
    showConfigureAppCredentials(appConfig);
    safeShowAlert(`Configurando ${app.name} para ${mockUserData.currentCompany.name}`, 'info');
}

function renderApplicationsList(applications) {
    const listContainer = document.getElementById('applicationsList');
    if (!listContainer) return;
    
    if (applications.length === 0) {
        listContainer.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-app-indicator" style="font-size: 3rem; color: var(--gray-400);"></i>
                <h5 class="mt-3 text-muted">Nenhuma aplicação encontrada</h5>
                <p class="text-muted">Crie a primeira aplicação para começar</p>
                <button class="btn btn-primary mt-2" onclick="showCreateApplication()">
                    <i class="bi bi-plus-circle me-2"></i>Nova Aplicação
                </button>
            </div>
        `;
        return;
    }
    
    const html = applications.map(app => `
        <div class="application-list-item mb-3" data-app-id="${app.id}">
            <div class="card">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-1">
                            <div class="application-icon">
                                <i class="bi bi-${getCategoryIcon(app.category)} text-primary"></i>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h5 class="mb-1">${app.name}</h5>
                            <p class="text-muted mb-0 small">${app.description}</p>
                        </div>
                        <div class="col-md-2">
                            <span class="badge bg-${getStatusColor(app.status)}">${getStatusText(app.status)}</span>
                            <br><small class="text-muted">${getCategoryText(app.category)}</small>
                        </div>
                        <div class="col-md-3">
                            <div class="credential-tags">
                                ${app.requiredCredentials.slice(0, 2).map(cred => 
                                    `<span class="badge bg-light text-dark me-1">${getCredentialText(cred)}</span>`
                                ).join('')}
                                ${app.requiredCredentials.length + (app.customCredentials ? app.customCredentials.length : 0) > 2 ? 
                                    `<span class="badge bg-secondary">+${app.requiredCredentials.length + (app.customCredentials ? app.customCredentials.length : 0) - 2}</span>` : ''}
                            </div>
                        </div>
                        <div class="col-md-2 text-end">
                            <button class="btn btn-outline-primary btn-sm me-1" onclick="editApplication('${app.id}')">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-primary btn-sm" onclick="configureApplication('${app.id}')">
                                <i class="bi bi-gear"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    listContainer.innerHTML = html;
}

function renderApplicationsTable(applications) {
    const tableBody = document.getElementById('applicationsTableBody');
    if (!tableBody) return;
    
    if (applications.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-4">
                    <i class="bi bi-app-indicator" style="font-size: 2rem; color: var(--gray-400);"></i>
                    <div class="mt-2 text-muted">Nenhuma aplicação encontrada</div>
                    <button class="btn btn-primary btn-sm mt-2" onclick="showCreateApplication()">
                        <i class="bi bi-plus-circle me-1"></i>Nova Aplicação
                    </button>
                </td>
            </tr>
        `;
        return;
    }
    
    const html = applications.map(app => {
        const createdDate = new Date(app.createdAt).toLocaleDateString('pt-BR');
        const credentialsCount = app.requiredCredentials.length + (app.customCredentials ? app.customCredentials.length : 0);
        
        return `
            <tr data-app-id="${app.id}">
                <td>
                    <div class="d-flex align-items-center">
                        <div class="application-icon me-3" style="width: 32px; height: 32px; font-size: 1rem;">
                            <i class="bi bi-${getCategoryIcon(app.category)} text-primary"></i>
                        </div>
                        <div>
                            <strong>${app.name}</strong>
                            <br><small class="text-muted">${app.description.substring(0, 50)}...</small>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge bg-light text-dark">${getCategoryText(app.category)}</span>
                </td>
                <td>
                    <span class="badge bg-${getStatusColor(app.status)}">${getStatusText(app.status)}</span>
                </td>
                <td>
                    <span class="badge bg-secondary">${credentialsCount} credenciais</span>
                </td>
                <td>
                    <small>${createdDate}</small>
                </td>
                <td>
                    <div class="btn-group" role="group">
                        <button class="btn btn-outline-primary btn-sm" onclick="editApplication('${app.id}')" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="configureApplication('${app.id}')" title="Configurar">
                            <i class="bi bi-gear"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
    
    tableBody.innerHTML = html;
}

// ===============================
// APLICAÇÕES DA EMPRESA
// ===============================

function showCompanyApplications() {
    console.log('🏢 Mostrar aplicações da empresa');
    hideAllScreens();
    document.getElementById('companyApplicationsScreen').classList.remove('d-none');
    setupCompanyViewToggle();
    loadCompanyApplications();
    updateCompanyAppSubtitle();
}

function setupCompanyViewToggle() {
    const viewToggle = document.querySelectorAll('input[name="companyViewMode"]');
    viewToggle.forEach(radio => {
        radio.addEventListener('change', (e) => {
            switchCompanyView(e.target.value);
        });
    });
}

function switchCompanyView(viewMode) {
    // Ocultar todas as visualizações
    document.getElementById('companyApplicationsGrid').classList.add('d-none');
    document.getElementById('companyApplicationsList').classList.add('d-none');
    document.getElementById('companyApplicationsTable').classList.add('d-none');
    
    // Mostrar visualização selecionada
    switch(viewMode) {
        case 'grid':
            document.getElementById('companyApplicationsGrid').classList.remove('d-none');
            renderCompanyApplicationsGrid(currentCompanyApplications);
            break;
        case 'list':
            document.getElementById('companyApplicationsList').classList.remove('d-none');
            renderCompanyApplicationsList(currentCompanyApplications);
            break;
        case 'table':
            document.getElementById('companyApplicationsTable').classList.remove('d-none');
            renderCompanyApplicationsTable(currentCompanyApplications);
            break;
    }
}

let currentCompanyApplications = [];

function loadCompanyApplications() {
    console.log('🏢 Carregando aplicações da empresa...');
    
    // Simular dados de aplicações configuradas pela empresa
    currentCompanyApplications = [
        {
            id: 'omie-mcp-config',
            applicationId: 'omie-mcp',
            name: 'Omie MCP',
            description: 'Integração MCP para Omie ERP com funcionalidades completas de gestão',
            category: 'mcp',
            status: 'active',
            lastConnection: '2025-01-10T14:30:00Z',
            configuredAt: '2024-12-15T10:00:00Z',
            credentials: {
                app_key: '****KEY',
                app_secret: '****SECRET'
            },
            settings: {
                enabled: true,
                notifications: true,
                notes: 'Configuração principal do ERP'
            }
        },
        {
            id: 'claude-mcp-config',
            applicationId: 'claude-mcp',
            name: 'Claude MCP Server',
            description: 'Servidor MCP para integração com Claude AI e automações inteligentes',
            category: 'ai',
            status: 'active',
            lastConnection: '2025-01-10T09:15:00Z',
            configuredAt: '2024-12-20T16:45:00Z',
            credentials: {
                token: '****TOKEN',
                api_url: 'https://api.claude.ai'
            },
            settings: {
                enabled: true,
                notifications: false,
                notes: 'Integração com IA para automações'
            }
        },
        {
            id: 'n8n-config',
            applicationId: 'n8n-automation',
            name: 'N8N Automation',
            description: 'Plataforma de automação de fluxos de trabalho e integrações',
            category: 'automation',
            status: 'pending',
            lastConnection: null,
            configuredAt: '2025-01-08T11:20:00Z',
            credentials: {
                email: 'admin@empresa.com',
                password: '****PASS',
                api_url: 'https://n8n.empresa.com',
                webhook_url: 'https://webhook.empresa.com/n8n'
            },
            settings: {
                enabled: false,
                notifications: true,
                notes: 'Aguardando configuração final dos webhooks'
            }
        },
        {
            id: 'financial-config',
            applicationId: 'financial-api',
            name: 'API Financeira',
            description: 'Integração com sistemas financeiros e bancários para automação',
            category: 'financial',
            status: 'error',
            lastConnection: '2025-01-09T08:30:00Z',
            configuredAt: '2024-12-10T14:15:00Z',
            credentials: {
                app_key: '****KEY',
                app_secret: '****SECRET',
                api_url: 'https://api.financeira.com'
            },
            settings: {
                enabled: true,
                notifications: true,
                notes: 'Erro de autenticação - verificar credenciais'
            }
        }
    ];
    
    // Atualizar estatísticas
    updateCompanyStats(currentCompanyApplications);
    
    // Renderizar na visualização atual
    const selectedView = document.querySelector('input[name="companyViewMode"]:checked').value;
    switchCompanyView(selectedView);
}

function updateCompanyAppSubtitle() {
    const subtitle = document.getElementById('companyAppSubtitle');
    const companyName = authManager?.currentCompany?.nome || 'Empresa Atual';
    if (subtitle) {
        subtitle.textContent = `Configure as integrações para ${companyName}`;
    }
}

function updateCompanyStats(applications) {
    const stats = {
        configured: applications.length,
        active: applications.filter(app => app.status === 'active').length,
        pending: applications.filter(app => app.status === 'pending').length,
        error: applications.filter(app => app.status === 'error').length
    };
    
    document.getElementById('statsConfigured').textContent = stats.configured;
    document.getElementById('statsActive').textContent = stats.active;
    document.getElementById('statsPending').textContent = stats.pending;
    document.getElementById('statsError').textContent = stats.error;
}

function renderCompanyApplicationsGrid(applications) {
    const grid = document.getElementById('companyApplicationsGrid');
    if (!grid) return;
    
    if (applications.length === 0) {
        grid.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-app-indicator" style="font-size: 3rem; color: var(--gray-400);"></i>
                <h5 class="mt-3 text-muted">Nenhuma aplicação configurada</h5>
                <p class="text-muted">Adicione aplicações para começar a usar as integrações</p>
                <button class="btn btn-primary mt-2" onclick="showAddApplicationToCompany()">
                    <i class="bi bi-plus-circle me-2"></i>Adicionar Aplicação
                </button>
            </div>
        `;
        return;
    }
    
    const html = applications.map(app => {
        const lastConnection = app.lastConnection ? 
            new Date(app.lastConnection).toLocaleString('pt-BR') : 'Nunca conectou';
        const credentialsCount = Object.keys(app.credentials).length;
        
        return `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card company-application-card h-100" data-app-id="${app.id}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div class="application-icon">
                                <i class="bi bi-${getCategoryIcon(app.category)} text-primary"></i>
                            </div>
                            <span class="badge bg-${getCompanyStatusColor(app.status)}">${getCompanyStatusText(app.status)}</span>
                        </div>
                        
                        <h5 class="card-title">${app.name}</h5>
                        <p class="card-text text-muted small">${app.description}</p>
                        
                        <div class="company-app-details mb-3">
                            <div class="row text-center">
                                <div class="col">
                                    <small class="text-muted d-block">Última Conexão</small>
                                    <strong class="small">${lastConnection}</strong>
                                </div>
                                <div class="col">
                                    <small class="text-muted d-block">Credenciais</small>
                                    <strong class="small">${credentialsCount}</strong>
                                </div>
                            </div>
                        </div>
                        
                        <div class="company-app-status mb-3">
                            <small class="text-muted d-block mb-1">Status da configuração:</small>
                            <div class="status-indicator">
                                <i class="bi bi-${getStatusIcon(app.status)} text-${getCompanyStatusColor(app.status)} me-1"></i>
                                <small>${getStatusDescription(app.status)}</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card-footer bg-transparent">
                        <div class="d-flex justify-content-between">
                            <button class="btn btn-outline-primary btn-sm" onclick="configureCompanyApplication('${app.id}')">
                                <i class="bi bi-gear me-1"></i>Configurar
                            </button>
                            <div class="btn-group">
                                <button class="btn btn-outline-info btn-sm" onclick="testCompanyAppConnection('${app.id}')" title="Testar">
                                    <i class="bi bi-wifi"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-sm" onclick="removeCompanyApplication('${app.id}')" title="Remover">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    grid.innerHTML = html;
}

function renderCompanyApplicationsList(applications) {
    const listContainer = document.getElementById('companyApplicationsList');
    if (!listContainer) return;
    
    if (applications.length === 0) {
        listContainer.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-app-indicator" style="font-size: 3rem; color: var(--gray-400);"></i>
                <h5 class="mt-3 text-muted">Nenhuma aplicação configurada</h5>
                <p class="text-muted">Adicione aplicações para começar a usar as integrações</p>
                <button class="btn btn-primary mt-2" onclick="showAddApplicationToCompany()">
                    <i class="bi bi-plus-circle me-2"></i>Adicionar Aplicação
                </button>
            </div>
        `;
        return;
    }
    
    const html = applications.map(app => {
        const lastConnection = app.lastConnection ? 
            new Date(app.lastConnection).toLocaleString('pt-BR') : 'Nunca conectou';
        const credentialsCount = Object.keys(app.credentials).length;
        
        return `
            <div class="company-application-list-item mb-3" data-app-id="${app.id}">
                <div class="card">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-1">
                                <div class="application-icon">
                                    <i class="bi bi-${getCategoryIcon(app.category)} text-primary"></i>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <h5 class="mb-1">${app.name}</h5>
                                <p class="text-muted mb-0 small">${app.description}</p>
                            </div>
                            <div class="col-md-2">
                                <span class="badge bg-${getCompanyStatusColor(app.status)}">${getCompanyStatusText(app.status)}</span>
                                <br><small class="text-muted">${getCategoryText(app.category)}</small>
                            </div>
                            <div class="col-md-3">
                                <small class="text-muted d-block">Última conexão:</small>
                                <small>${lastConnection}</small>
                            </div>
                            <div class="col-md-2 text-end">
                                <button class="btn btn-primary btn-sm me-1" onclick="configureCompanyApplication('${app.id}')">
                                    <i class="bi bi-gear"></i>
                                </button>
                                <button class="btn btn-outline-info btn-sm me-1" onclick="testCompanyAppConnection('${app.id}')">
                                    <i class="bi bi-wifi"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-sm" onclick="removeCompanyApplication('${app.id}')">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    listContainer.innerHTML = html;
}

function renderCompanyApplicationsTable(applications) {
    const tableBody = document.getElementById('companyApplicationsTableBody');
    if (!tableBody) return;
    
    if (applications.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-4">
                    <i class="bi bi-app-indicator" style="font-size: 2rem; color: var(--gray-400);"></i>
                    <div class="mt-2 text-muted">Nenhuma aplicação configurada</div>
                    <button class="btn btn-primary btn-sm mt-2" onclick="showAddApplicationToCompany()">
                        <i class="bi bi-plus-circle me-1"></i>Adicionar Aplicação
                    </button>
                </td>
            </tr>
        `;
        return;
    }
    
    const html = applications.map(app => {
        const lastConnection = app.lastConnection ? 
            new Date(app.lastConnection).toLocaleString('pt-BR') : 'Nunca conectou';
        const configuredDate = new Date(app.configuredAt).toLocaleDateString('pt-BR');
        const credentialsCount = Object.keys(app.credentials).length;
        
        return `
            <tr data-app-id="${app.id}">
                <td>
                    <div class="d-flex align-items-center">
                        <div class="application-icon me-3" style="width: 32px; height: 32px; font-size: 1rem;">
                            <i class="bi bi-${getCategoryIcon(app.category)} text-primary"></i>
                        </div>
                        <div>
                            <strong>${app.name}</strong>
                            <br><small class="text-muted">${app.description.substring(0, 40)}...</small>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge bg-${getCompanyStatusColor(app.status)}">${getCompanyStatusText(app.status)}</span>
                </td>
                <td>
                    <small>${lastConnection}</small>
                </td>
                <td>
                    <span class="badge bg-secondary">${credentialsCount} credenciais</span>
                </td>
                <td>
                    <small>${configuredDate}</small>
                </td>
                <td>
                    <div class="btn-group" role="group">
                        <button class="btn btn-primary btn-sm" onclick="configureCompanyApplication('${app.id}')" title="Configurar">
                            <i class="bi bi-gear"></i>
                        </button>
                        <button class="btn btn-outline-info btn-sm" onclick="testCompanyAppConnection('${app.id}')" title="Testar">
                            <i class="bi bi-wifi"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="removeCompanyApplication('${app.id}')" title="Remover">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
    
    tableBody.innerHTML = html;
}

function getCompanyStatusColor(status) {
    const colors = {
        'active': 'success',
        'pending': 'warning',
        'error': 'danger',
        'inactive': 'secondary'
    };
    return colors[status] || 'secondary';
}

function getCompanyStatusText(status) {
    const texts = {
        'active': 'Ativo',
        'pending': 'Pendente',
        'error': 'Erro',
        'inactive': 'Inativo'
    };
    return texts[status] || status;
}

function getStatusIcon(status) {
    const icons = {
        'active': 'check-circle-fill',
        'pending': 'clock-fill',
        'error': 'exclamation-triangle-fill',
        'inactive': 'dash-circle-fill'
    };
    return icons[status] || 'question-circle-fill';
}

function getStatusDescription(status) {
    const descriptions = {
        'active': 'Funcionando corretamente',
        'pending': 'Aguardando configuração',
        'error': 'Erro na conexão',
        'inactive': 'Desativada'
    };
    return descriptions[status] || 'Status desconhecido';
}

function filterCompanyApplications() {
    console.log('🔍 Filtrar aplicações da empresa...');
    const search = document.getElementById('searchCompanyApps').value;
    const category = document.getElementById('filterCompanyCategory').value;
    const status = document.getElementById('filterCompanyStatus').value;
    
    console.log('Filtros da empresa:', { search, category, status });
    safeShowAlert('Filtros aplicados!', 'info');
}

function showAddApplicationToCompany() {
    console.log('➕ Adicionar aplicação à empresa...');
    
    // Redirecionar para o catálogo de aplicações
    showApplications();
    
    // Mostrar mensagem informativa
    setTimeout(() => {
        safeShowAlert('💡 Dica: Use o catálogo para explorar e adicionar novas aplicações à sua empresa!', 'info');
    }, 500);
}

function configureCompanyApplication(appConfigId) {
    console.log('⚙️ Configurar aplicação da empresa:', appConfigId);
    console.log('📋 Aplicações da empresa disponíveis:', currentCompanyApplications.map(app => app.id));
    
    // Garantir que temos dados carregados
    if (!currentCompanyApplications || currentCompanyApplications.length === 0) {
        console.warn('⚠️ Dados não carregados, recarregando...');
        loadCompanyApplications();
    }
    
    // Encontrar a aplicação
    const appConfig = currentCompanyApplications.find(app => app.id === appConfigId);
    console.log('🔍 Aplicação encontrada:', appConfig);
    
    if (!appConfig) {
        console.error('❌ Aplicação não encontrada:', appConfigId);
        safeShowAlert('Aplicação não encontrada', 'danger');
        return;
    }
    
    // Ir para tela de configuração
    showConfigureAppCredentials(appConfig);
}

function testCompanyAppConnection(appConfigId) {
    console.log('🧪 Testar conexão:', appConfigId);
    safeShowAlert('Testando conexão...', 'info');
    
    // Simular teste de conexão
    setTimeout(() => {
        safeShowAlert('Conexão testada com sucesso!', 'success');
    }, 2000);
}

function removeCompanyApplication(appConfigId) {
    if (confirm('Tem certeza que deseja remover esta aplicação? Todas as configurações serão perdidas.')) {
        console.log('🗑️ Remover aplicação da empresa:', appConfigId);
        safeShowAlert('Aplicação removida com sucesso!', 'success');
        
        // Simular remoção
        setTimeout(() => {
            loadCompanyApplications();
        }, 1000);
    }
}

// ===============================
// CONFIGURAÇÃO DE CREDENCIAIS
// ===============================

function showConfigureAppCredentials(appConfig) {
    console.log('⚙️ Mostrar configuração de credenciais para:', appConfig);
    console.log('📋 Aplicações disponíveis:', mockApplications.map(app => app.id));
    
    hideAllScreens();
    document.getElementById('configureAppCredentialsScreen').classList.remove('d-none');
    
    // Encontrar aplicação original no catálogo
    const originalApp = mockApplications.find(app => app.id === appConfig.applicationId);
    console.log('🔍 Aplicação encontrada:', originalApp);
    
    if (!originalApp) {
        console.error('❌ Aplicação não encontrada:', appConfig.applicationId);
        safeShowAlert('Aplicação não encontrada no catálogo', 'danger');
        return;
    }
    
    // Preencher informações da aplicação
    document.getElementById('configAppName').textContent = originalApp.name;
    document.getElementById('configAppDescription').textContent = originalApp.description;
    document.getElementById('configAppCategory').textContent = originalApp.category;
    document.getElementById('configAppIcon').innerHTML = `<i class="bi bi-${originalApp.icon}"></i>`;
    
    // Preencher configurações atuais
    document.getElementById('configAppStatus').textContent = getCompanyStatusText(appConfig.status);
    document.getElementById('configAppLastConnection').textContent = 
        appConfig.lastConnection ? formatDate(appConfig.lastConnection) : 'Nunca';
    
    // Gerar campos de credenciais
    generateCredentialFields(originalApp, appConfig);
    
    // Preencher configurações avançadas
    fillAdvancedSettings(appConfig);
    
    // Configurar listeners
    setupCredentialsFormListeners(appConfig);
}

function generateCredentialFields(application, currentConfig) {
    const container = document.getElementById('credentialsFields');
    const credentials = currentConfig.credentials || {};
    
    let html = '';
    
    // Gerar campos baseados nos requisitos da aplicação
    application.requiredCredentials.forEach(field => {
        const value = credentials[field.key] || '';
        const fieldId = `cred_${field.key}`;
        
        html += `
            <div class="credentials-field">
                <label for="${fieldId}" class="form-label">
                    ${field.label}
                    ${field.required ? '<span class="text-danger">*</span>' : ''}
                </label>
                ${generateFieldInput(field, fieldId, value)}
                ${field.description ? `<div class="form-text">${field.description}</div>` : ''}
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function generateFieldInput(field, fieldId, value) {
    const commonAttrs = `id="${fieldId}" name="${field.key}" class="form-control"`;
    const requiredAttr = field.required ? 'required' : '';
    
    switch (field.type) {
        case 'password':
            return `
                <div class="input-group">
                    <input type="password" ${commonAttrs} ${requiredAttr} value="${value}" 
                           placeholder="${field.placeholder || ''}">
                    <button class="btn btn-outline-secondary" type="button" onclick="togglePasswordVisibility('${fieldId}')">
                        <i class="bi bi-eye" id="${fieldId}_toggle"></i>
                    </button>
                </div>
            `;
        case 'url':
            return `<input type="url" ${commonAttrs} ${requiredAttr} value="${value}" 
                           placeholder="${field.placeholder || 'https://'}">`;
        case 'email':
            return `<input type="email" ${commonAttrs} ${requiredAttr} value="${value}" 
                           placeholder="${field.placeholder || 'exemplo@dominio.com'}">`;
        case 'select':
            const options = field.options.map(opt => 
                `<option value="${opt.value}" ${opt.value === value ? 'selected' : ''}>${opt.label}</option>`
            ).join('');
            return `<select ${commonAttrs} ${requiredAttr}>${options}</select>`;
        case 'textarea':
            return `<textarea ${commonAttrs} ${requiredAttr} rows="3" placeholder="${field.placeholder || ''}">${value}</textarea>`;
        default:
            return `<input type="text" ${commonAttrs} ${requiredAttr} value="${value}" 
                           placeholder="${field.placeholder || ''}">`;
    }
}

function fillAdvancedSettings(appConfig) {
    const settings = appConfig.settings || {};
    
    // Preencher configurações avançadas
    document.getElementById('appEnabled').checked = settings.enabled !== false;
    document.getElementById('appNotifications').checked = settings.notifications !== false;
    document.getElementById('appLogging').checked = settings.logging !== false;
    document.getElementById('appTimeout').value = settings.timeout || '30';
    document.getElementById('appRetries').value = settings.retries || '3';
    document.getElementById('appNotes').value = settings.notes || '';
}

function setupCredentialsFormListeners(appConfig) {
    const form = document.getElementById('credentialsForm');
    
    // Remover listeners anteriores
    form.removeEventListener('submit', handleCredentialsSubmit);
    
    // Adicionar novo listener
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        handleCredentialsSubmit(appConfig);
    });
    
    // Botão de teste
    const testBtn = document.getElementById('testCredentialsBtn');
    if (testBtn) {
        testBtn.onclick = () => testCredentials(appConfig);
    }
    
    // Botões de voltar (header e footer)
    const backBtnHeader = document.getElementById('backToCompanyAppsHeader');
    const backBtnFooter = document.getElementById('backToCompanyAppsBtn');
    
    if (backBtnHeader) {
        backBtnHeader.onclick = () => {
            console.log('🔙 Voltar para aplicações da empresa (header)');
            showCompanyApplications();
        };
    }
    
    if (backBtnFooter) {
        backBtnFooter.onclick = () => {
            console.log('🔙 Voltar para aplicações da empresa (footer)');
            showCompanyApplications();
        };
    }
}

function handleCredentialsSubmit(appConfig) {
    console.log('💾 Salvar credenciais para:', appConfig.id);
    
    // Coletar dados do formulário
    const formData = new FormData(document.getElementById('credentialsForm'));
    const credentials = {};
    const settings = {};
    
    // Processar credenciais
    for (const [key, value] of formData.entries()) {
        if (key.startsWith('cred_')) {
            credentials[key.replace('cred_', '')] = value;
        } else {
            settings[key] = value;
        }
    }
    
    // Processar checkboxes
    settings.enabled = document.getElementById('appEnabled').checked;
    settings.notifications = document.getElementById('appNotifications').checked;
    settings.logging = document.getElementById('appLogging').checked;
    
    // Validar campos obrigatórios
    const originalApp = mockApplications.find(app => app.id === appConfig.applicationId);
    const missingFields = [];
    
    originalApp.requiredCredentials.forEach(field => {
        if (field.required && !credentials[field.key]) {
            missingFields.push(field.label);
        }
    });
    
    if (missingFields.length > 0) {
        safeShowAlert(`Campos obrigatórios não preenchidos: ${missingFields.join(', ')}`, 'danger');
        return;
    }
    
    // Simular salvamento
    safeShowAlert('Salvando configurações...', 'info');
    
    setTimeout(() => {
        // Atualizar configuração
        const configIndex = currentCompanyApplications.findIndex(app => app.id === appConfig.id);
        if (configIndex !== -1) {
            currentCompanyApplications[configIndex] = {
                ...currentCompanyApplications[configIndex],
                credentials,
                settings,
                status: 'active',
                lastConnection: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
        }
        
        safeShowAlert('Configurações salvas com sucesso!', 'success');
        
        // Voltar para tela anterior após 2 segundos
        setTimeout(() => {
            showCompanyApplications();
        }, 2000);
    }, 1500);
}

function testCredentials(appConfig) {
    console.log('🧪 Testar credenciais para:', appConfig.id);
    
    safeShowAlert('Testando credenciais...', 'info');
    
    // Simular teste de conexão
    setTimeout(() => {
        const success = Math.random() > 0.3; // 70% de sucesso
        
        if (success) {
            safeShowAlert('✅ Credenciais válidas! Conexão estabelecida com sucesso.', 'success');
            
            // Atualizar status para ativo
            const configIndex = currentCompanyApplications.findIndex(app => app.id === appConfig.id);
            if (configIndex !== -1) {
                currentCompanyApplications[configIndex].status = 'active';
                currentCompanyApplications[configIndex].lastConnection = new Date().toISOString();
            }
        } else {
            safeShowAlert('❌ Falha na conexão. Verifique as credenciais e tente novamente.', 'danger');
            
            // Atualizar status para erro
            const configIndex = currentCompanyApplications.findIndex(app => app.id === appConfig.id);
            if (configIndex !== -1) {
                currentCompanyApplications[configIndex].status = 'error';
            }
        }
    }, 3000);
}

function togglePasswordVisibility(fieldId) {
    const field = document.getElementById(fieldId);
    const toggle = document.getElementById(`${fieldId}_toggle`);
    
    if (field.type === 'password') {
        field.type = 'text';
        toggle.className = 'bi bi-eye-slash';
    } else {
        field.type = 'password';
        toggle.className = 'bi bi-eye';
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR') + ' às ' + date.toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

function showCredentialsHelp() {
    const helpContent = `
🔧 AJUDA - CONFIGURAÇÃO DE CREDENCIAIS

📋 Como configurar:
1. Preencha todas as credenciais obrigatórias (marcadas com *)
2. Configure as opções avançadas conforme necessário
3. Use "Testar Conexão" para validar
4. Salve as configurações

🔑 Tipos de Campo:
• Senha: Use o botão 👁️ para mostrar/ocultar
• URL: Deve começar com http:// ou https://
• Email: Formato válido necessário
• Número: Apenas valores numéricos

⚙️ Configurações Avançadas:
• Timeout: Tempo limite para conexões (5-300 segundos)
• Tentativas: Número de retry em caso de falha (0-10)
• Logs: Habilita registro detalhado de atividades

🧪 Teste de Conexão:
Valida se as credenciais estão corretas e a aplicação responde adequadamente.

💡 Dicas:
- Mantenha suas credenciais seguras
- Teste regularmente as conexões
- Use notas para documentar configurações especiais
    `;
    alert(helpContent);
}

// ===============================
// NAVEGAÇÃO DO DASHBOARD
// ===============================

function showDashboard() {
    console.log('🏠 Mostrar dashboard principal');
    hideAllScreens();
    document.getElementById('dashboardScreen').classList.remove('d-none');
    
    // Atualizar estatísticas do dashboard
    updateDashboardStats();
}

function updateDashboardStats() {
    // Simular atualização das estatísticas
    const stats = {
        configuredApps: currentCompanyApplications ? currentCompanyApplications.length : 4,
        activeApps: currentCompanyApplications ? currentCompanyApplications.filter(app => app.status === 'active').length : 3,
        activeUsers: 5,
        monthlyConnections: Math.floor(Math.random() * 1000) + 500
    };
    
    // Atualizar elementos no DOM
    const configuredElement = document.getElementById('configuredApps');
    const activeElement = document.getElementById('activeApps');
    const usersElement = document.getElementById('activeUsers');
    const connectionsElement = document.getElementById('monthlyConnections');
    
    if (configuredElement) configuredElement.textContent = stats.configuredApps;
    if (activeElement) activeElement.textContent = stats.activeApps;
    if (usersElement) usersElement.textContent = stats.activeUsers;
    if (connectionsElement) connectionsElement.textContent = stats.monthlyConnections;
}