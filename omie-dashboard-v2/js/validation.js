/**
 * Validações em tempo real para formulários
 */

class ValidationManager {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8003'; // Tenant Manager API
        this.debounceTimer = null;
    }

    // Validação de email único
    async validateEmailUnique(email) {
        if (!email || !this.isValidEmail(email)) {
            return { valid: false, message: 'Email inválido' };
        }

        try {
            // Tentar validar no backend primeiro
            if (window.authManager && window.authManager.backend) {
                try {
                    const response = await window.authManager.backend.validateEmail(email);
                    if (response.success !== undefined) {
                        return {
                            valid: response.success,
                            message: response.message || (response.success ? 'Email disponível' : 'Email já cadastrado')
                        };
                    }
                } catch (backendError) {
                    console.warn('⚠️ Erro na validação de email no backend:', backendError.message);
                }
            }
            
            // Fallback para validação local
            const existingEmails = ['joao.silva@teste.com'];
            
            if (existingEmails.includes(email.toLowerCase())) {
                return { valid: false, message: 'Este email já está cadastrado' };
            }
            
            return { valid: true, message: 'Email disponível' };
            
        } catch (error) {
            console.error('Erro ao validar email:', error);
            return { valid: true, message: 'Não foi possível validar (continuando)' };
        }
    }

    // Validação de CNPJ único
    async validateCNPJUnique(cnpj) {
        if (!cnpj || !this.isValidCNPJ(cnpj)) {
            return { valid: false, message: 'CNPJ inválido' };
        }

        try {
            // Tentar validar no backend primeiro
            if (window.authManager && window.authManager.backend) {
                try {
                    const response = await window.authManager.backend.validateCNPJ(cnpj);
                    if (response.success !== undefined) {
                        return {
                            valid: response.success,
                            message: response.message || (response.success ? 'CNPJ disponível' : 'CNPJ já cadastrado')
                        };
                    }
                } catch (backendError) {
                    console.warn('⚠️ Erro na validação de CNPJ no backend:', backendError.message);
                }
            }
            
            // Fallback para validação local
            const existingCNPJs = ['46845239000163', '12345678000195'];
            const cleanCNPJ = cnpj.replace(/\D/g, '');
            
            if (existingCNPJs.includes(cleanCNPJ)) {
                return { valid: false, message: 'Este CNPJ já está cadastrado' };
            }
            
            return { valid: true, message: 'CNPJ disponível' };
            
        } catch (error) {
            console.error('Erro ao validar CNPJ:', error);
            return { valid: true, message: 'Não foi possível validar (continuando)' };
        }
    }

    // Validação de email com debounce
    setupEmailValidation(emailInputId, statusElementId) {
        const emailInput = document.getElementById(emailInputId);
        const statusElement = document.getElementById(statusElementId);
        
        if (!emailInput) return;

        emailInput.addEventListener('input', (e) => {
            const email = e.target.value.trim();
            
            // Limpar timer anterior
            if (this.debounceTimer) {
                clearTimeout(this.debounceTimer);
            }
            
            // Validar após 500ms de inatividade
            this.debounceTimer = setTimeout(async () => {
                if (email.length > 0) {
                    const result = await this.validateEmailUnique(email);
                    this.updateValidationStatus(statusElement, result, emailInput);
                } else {
                    this.clearValidationStatus(statusElement, emailInput);
                }
            }, 500);
        });
    }

    // Validação de CNPJ com debounce
    setupCNPJValidation(cnpjInputId, statusElementId) {
        const cnpjInput = document.getElementById(cnpjInputId);
        const statusElement = document.getElementById(statusElementId);
        
        if (!cnpjInput) return;

        cnpjInput.addEventListener('input', (e) => {
            const cnpj = e.target.value.trim();
            
            // Limpar timer anterior
            if (this.debounceTimer) {
                clearTimeout(this.debounceTimer);
            }
            
            // Validar após 800ms de inatividade
            this.debounceTimer = setTimeout(async () => {
                if (cnpj.length >= 14) {
                    const result = await this.validateCNPJUnique(cnpj);
                    this.updateValidationStatus(statusElement, result, cnpjInput);
                } else {
                    this.clearValidationStatus(statusElement, cnpjInput);
                }
            }, 800);
        });
    }

    // Atualizar status visual da validação
    updateValidationStatus(statusElement, result, inputElement) {
        if (!statusElement) return;

        // Remover classes anteriores
        inputElement?.classList.remove('is-valid', 'is-invalid');
        
        if (result.valid) {
            statusElement.innerHTML = `<span class="text-success"><i class="bi bi-check-circle me-1"></i>${result.message}</span>`;
            inputElement?.classList.add('is-valid');
        } else {
            statusElement.innerHTML = `<span class="text-danger"><i class="bi bi-x-circle me-1"></i>${result.message}</span>`;
            inputElement?.classList.add('is-invalid');
        }
    }

    // Limpar status de validação
    clearValidationStatus(statusElement, inputElement) {
        if (statusElement) {
            statusElement.innerHTML = '<span class="text-muted">Digite para validar</span>';
        }
        inputElement?.classList.remove('is-valid', 'is-invalid');
    }

    // Validações básicas
    isValidEmail(email) {
        const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return pattern.test(email);
    }

    isValidCNPJ(cnpj) {
        cnpj = cnpj.replace(/\D/g, '');
        
        if (cnpj.length !== 14) return false;
        if (/^(\d)\1{13}$/.test(cnpj)) return false; // Todos iguais
        
        // Validação matemática do CNPJ
        let tamanho = cnpj.length - 2;
        let numeros = cnpj.substring(0, tamanho);
        let digitos = cnpj.substring(tamanho);
        let soma = 0;
        let pos = tamanho - 7;
        
        for (let i = tamanho; i >= 1; i--) {
            soma += numeros.charAt(tamanho - i) * pos--;
            if (pos < 2) pos = 9;
        }
        
        let resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
        if (resultado != digitos.charAt(0)) return false;
        
        tamanho = tamanho + 1;
        numeros = cnpj.substring(0, tamanho);
        soma = 0;
        pos = tamanho - 7;
        
        for (let i = tamanho; i >= 1; i--) {
            soma += numeros.charAt(tamanho - i) * pos--;
            if (pos < 2) pos = 9;
        }
        
        resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
        return resultado == digitos.charAt(1);
    }

    // Configurar validações em todos os formulários
    setupAllValidations() {
        // Formulário de cadastro de usuário
        this.setupEmailValidation('registerEmail', 'registerEmailStatus');
        
        // Formulário de criação de empresa
        this.setupCNPJValidation('companyCNPJ', 'cnpjStatus');
        this.setupEmailValidation('companyEmail', 'companyEmailStatus');
        
        // Formulário de convite
        this.setupEmailValidation('inviteEmail', 'inviteEmailStatus');
        
        console.log('✅ Validações em tempo real configuradas');
    }

    // Validar formulário antes do submit
    async validateFormBeforeSubmit(formData, formType) {
        const errors = [];
        
        if (formType === 'register' && formData.email) {
            const emailResult = await this.validateEmailUnique(formData.email);
            if (!emailResult.valid) {
                errors.push(`Email: ${emailResult.message}`);
            }
        }
        
        if (formType === 'company' && formData.cnpj) {
            const cnpjResult = await this.validateCNPJUnique(formData.cnpj);
            if (!cnpjResult.valid) {
                errors.push(`CNPJ: ${cnpjResult.message}`);
            }
        }
        
        if (formType === 'company' && formData.email) {
            const emailResult = await this.validateEmailUnique(formData.email);
            if (!emailResult.valid) {
                errors.push(`Email da empresa: ${emailResult.message}`);
            }
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
}

// Instância global
const validationManager = new ValidationManager();

// Configurar validações quando DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    validationManager.setupAllValidations();
});

// Disponibilizar globalmente
window.validationManager = validationManager;