/**
 * Módulo de Segurança v2.0
 * Implementa todas as melhores práticas de segurança para aplicação de tokens
 */

class SecurityManager {
    constructor() {
        this.sessionTimeout = 30 * 60 * 1000; // 30 minutos
        this.maxLoginAttempts = 5;
        this.lockoutDuration = 15 * 60 * 1000; // 15 minutos
        this.tokenPrefix = 'omt_';
        this.init();
    }

    init() {
        try {
            this.setupSecurityHeaders();
            this.setupSessionManagement();
            this.setupInputSanitization();
            this.setupSecurityMonitoring();
            this.preventClickjacking();
            this.setupCSRFProtection();
            console.log('✅ SecurityManager inicializado com sucesso');
        } catch (error) {
            console.error('❌ Erro ao inicializar SecurityManager:', error);
        }
    }

    // ===============================
    // TOKEN SECURITY
    // ===============================

    /**
     * Gera token seguro com entropia alta
     */
    generateSecureToken(length = 32) {
        const array = new Uint8Array(length);
        crypto.getRandomValues(array);
        return this.tokenPrefix + Array.from(array, byte => 
            byte.toString(16).padStart(2, '0')
        ).join('');
    }

    /**
     * Armazena token de forma segura
     */
    storeTokenSecurely(token, expiresIn = this.sessionTimeout) {
        const tokenData = {
            token: token,
            expires: Date.now() + expiresIn,
            fingerprint: this.generateFingerprint(),
            issued: Date.now()
        };

        // Criptografar antes de armazenar
        const encryptedData = this.encryptData(JSON.stringify(tokenData));
        
        try {
            sessionStorage.setItem('secure_token', encryptedData);
            
            // Log de segurança
            this.logSecurityEvent('token_stored', {
                fingerprint: tokenData.fingerprint,
                expires: new Date(tokenData.expires).toISOString()
            });
        } catch (error) {
            console.error('Erro ao armazenar token:', error);
            throw new Error('Falha ao armazenar credenciais de forma segura');
        }
    }

    /**
     * Recupera token de forma segura
     */
    getSecureToken() {
        try {
            const encryptedData = sessionStorage.getItem('secure_token');
            if (!encryptedData) return null;

            const decryptedData = this.decryptData(encryptedData);
            const tokenData = JSON.parse(decryptedData);

            // Verificar expiração
            if (Date.now() > tokenData.expires) {
                this.clearSecureToken();
                this.logSecurityEvent('token_expired');
                return null;
            }

            // Verificar fingerprint
            if (tokenData.fingerprint !== this.generateFingerprint()) {
                this.clearSecureToken();
                this.logSecurityEvent('fingerprint_mismatch', { 
                    stored: tokenData.fingerprint,
                    current: this.generateFingerprint()
                });
                throw new Error('Sessão comprometida detectada');
            }

            return tokenData.token;
        } catch (error) {
            console.error('Erro ao recuperar token:', error);
            this.clearSecureToken();
            return null;
        }
    }

    /**
     * Remove token de forma segura
     */
    clearSecureToken() {
        sessionStorage.removeItem('secure_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('current_company');
        
        // Limpar outros dados sensíveis
        this.clearSensitiveData();
        
        this.logSecurityEvent('token_cleared');
    }

    // ===============================
    // CRIPTOGRAFIA
    // ===============================

    /**
     * Criptografia simples (para demonstração - usar biblioteca robusta em produção)
     */
    encryptData(data) {
        // Em produção, usar Web Crypto API ou biblioteca como crypto-js
        const key = this.getEncryptionKey();
        return btoa(data + '|' + key);
    }

    decryptData(encryptedData) {
        try {
            const decoded = atob(encryptedData);
            const [data, key] = decoded.split('|');
            
            if (key !== this.getEncryptionKey()) {
                throw new Error('Chave de criptografia inválida');
            }
            
            return data;
        } catch (error) {
            throw new Error('Falha ao descriptografar dados');
        }
    }

    getEncryptionKey() {
        return btoa(navigator.userAgent + window.location.hostname);
    }

    // ===============================
    // FINGERPRINTING
    // ===============================

    /**
     * Gera fingerprint único do cliente
     */
    generateFingerprint() {
        const components = [
            navigator.userAgent,
            navigator.language,
            screen.width + 'x' + screen.height,
            new Date().getTimezoneOffset(),
            window.location.hostname,
            navigator.platform
        ];

        return this.hash(components.join('|'));
    }

    hash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return hash.toString(36);
    }

    // ===============================
    // GERENCIAMENTO DE SESSÃO
    // ===============================

    setupSessionManagement() {
        // Auto-logout por inatividade
        let inactivityTimer;
        
        const resetTimer = () => {
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(() => {
                this.handleSessionTimeout();
            }, this.sessionTimeout);
        };

        // Eventos que indicam atividade
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'].forEach(event => {
            document.addEventListener(event, resetTimer, true);
        });

        // Iniciar timer
        resetTimer();

        // Detectar múltiplas abas
        window.addEventListener('storage', (e) => {
            if (e.key === 'tab_check') {
                this.handleMultipleTabsDetected();
            }
        });

        // Detectar fechamento da aba
        window.addEventListener('beforeunload', () => {
            this.logSecurityEvent('session_ended');
        });
    }

    handleSessionTimeout() {
        this.clearSecureToken();
        this.logSecurityEvent('session_timeout');
        
        if (typeof authManager !== 'undefined') {
            authManager.showAlert('Sessão expirada por inatividade. Faça login novamente.', 'warning');
            authManager.showWelcome();
        }
    }

    handleMultipleTabsDetected() {
        this.logSecurityEvent('multiple_tabs_detected');
        
        if (typeof authManager !== 'undefined') {
            authManager.showAlert('Múltiplas abas detectadas. Por segurança, faça login novamente.', 'warning');
            this.clearSecureToken();
            authManager.showWelcome();
        }
    }

    // ===============================
    // PROTEÇÃO CONTRA ATAQUES
    // ===============================

    setupInputSanitization() {
        // Sanitizar todos os inputs automaticamente
        document.addEventListener('input', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                this.sanitizeInput(e.target);
            }
        });
    }

    sanitizeInput(input) {
        const originalValue = input.value;
        
        // Remover scripts maliciosos
        let sanitized = originalValue
            .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
            .replace(/javascript:/gi, '')
            .replace(/on\w+\s*=/gi, '');

        // Escapar HTML se necessário
        if (input.dataset.allowHtml !== 'true') {
            sanitized = this.escapeHtml(sanitized);
        }

        if (sanitized !== originalValue) {
            input.value = sanitized;
            this.logSecurityEvent('input_sanitized', { 
                field: input.name || input.id,
                original: originalValue.length,
                sanitized: sanitized.length
            });
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Proteção contra login brute force
     */
    checkLoginAttempts(email) {
        const key = `login_attempts_${this.hash(email)}`;
        const attempts = JSON.parse(localStorage.getItem(key) || '[]');
        const now = Date.now();
        
        // Remover tentativas antigas (mais de 1 hora)
        const recentAttempts = attempts.filter(attempt => 
            now - attempt < 60 * 60 * 1000
        );

        if (recentAttempts.length >= this.maxLoginAttempts) {
            const lastAttempt = Math.max(...recentAttempts);
            const lockoutEnd = lastAttempt + this.lockoutDuration;
            
            if (now < lockoutEnd) {
                const remainingTime = Math.ceil((lockoutEnd - now) / 60000);
                throw new Error(`Conta bloqueada. Tente novamente em ${remainingTime} minutos.`);
            }
        }

        return true;
    }

    recordLoginAttempt(email, success = false) {
        const key = `login_attempts_${this.hash(email)}`;
        
        if (success) {
            // Limpar tentativas em caso de sucesso
            localStorage.removeItem(key);
            this.logSecurityEvent('login_success', { email });
        } else {
            // Registrar tentativa falhada
            const attempts = JSON.parse(localStorage.getItem(key) || '[]');
            attempts.push(Date.now());
            localStorage.setItem(key, JSON.stringify(attempts));
            
            this.logSecurityEvent('login_failed', { 
                email, 
                attempts: attempts.length 
            });
        }
    }

    // ===============================
    // PROTEÇÕES ADICIONAIS
    // ===============================

    preventClickjacking() {
        // Verificar se está sendo executado em iframe
        if (window.top !== window.self) {
            document.body.style.display = 'none';
            throw new Error('Aplicação não pode ser executada em iframe');
        }
    }

    setupCSRFProtection() {
        // Gerar token CSRF único para cada sessão
        const csrfToken = this.generateSecureToken(16);
        sessionStorage.setItem('csrf_token', csrfToken);
        
        // Adicionar token a todos os formulários
        document.addEventListener('submit', (e) => {
            if (e.target.tagName === 'FORM') {
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = '_csrf_token';
                hiddenInput.value = csrfToken;
                e.target.appendChild(hiddenInput);
            }
        });
    }

    setupSecurityHeaders() {
        // Verificar se headers de segurança estão sendo aplicados
        if (document.location.protocol !== 'https:' && 
            document.location.hostname !== 'localhost') {
            console.warn('Aplicação deve ser servida via HTTPS em produção');
        }
    }

    // ===============================
    // MONITORAMENTO E LOGS
    // ===============================

    setupSecurityMonitoring() {
        // Detectar tentativas de debugging
        let devtools = false;
        setInterval(() => {
            if (window.outerHeight - window.innerHeight > 200 || 
                window.outerWidth - window.innerWidth > 200) {
                if (!devtools) {
                    devtools = true;
                    this.logSecurityEvent('devtools_opened');
                }
            } else {
                devtools = false;
            }
        }, 1000);

        // Detectar copy/paste de senhas
        document.addEventListener('paste', (e) => {
            if (e.target.type === 'password') {
                this.logSecurityEvent('password_pasted');
            }
        });
    }

    logSecurityEvent(event, data = {}) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            event,
            data,
            fingerprint: this.generateFingerprint(),
            userAgent: navigator.userAgent,
            url: window.location.href
        };

        // Em produção, enviar para servidor de logs
        console.log('Security Event:', logEntry);
        
        // Armazenar localmente para debug
        const logs = JSON.parse(localStorage.getItem('security_logs') || '[]');
        logs.push(logEntry);
        
        // Manter apenas os últimos 100 logs
        if (logs.length > 100) {
            logs.splice(0, logs.length - 100);
        }
        
        localStorage.setItem('security_logs', JSON.stringify(logs));
    }

    // ===============================
    // LIMPEZA DE DADOS SENSÍVEIS
    // ===============================

    clearSensitiveData() {
        // Limpar dados sensíveis do DOM
        const sensitiveInputs = document.querySelectorAll('input[type="password"], input[type="email"]');
        sensitiveInputs.forEach(input => {
            input.value = '';
        });

        // Limpar variáveis globais sensíveis
        if (window.authManager) {
            window.authManager.currentUser = null;
            window.authManager.currentCompany = null;
        }
    }

    // ===============================
    // UTILITÁRIOS PÚBLICOS
    // ===============================

    validatePassword(password) {
        const minLength = 8;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        const errors = [];
        
        if (password.length < minLength) {
            errors.push(`Senha deve ter pelo menos ${minLength} caracteres`);
        }
        if (!hasUpperCase) {
            errors.push('Senha deve conter pelo menos uma letra maiúscula');
        }
        if (!hasLowerCase) {
            errors.push('Senha deve conter pelo menos uma letra minúscula');
        }
        if (!hasNumbers) {
            errors.push('Senha deve conter pelo menos um número');
        }
        if (!hasSpecialChar) {
            errors.push('Senha deve conter pelo menos um caractere especial');
        }

        return {
            isValid: errors.length === 0,
            errors,
            score: this.calculatePasswordScore(password)
        };
    }

    calculatePasswordScore(password) {
        let score = 0;
        
        // Comprimento
        score += Math.min(password.length * 2, 20);
        
        // Variedade de caracteres
        if (/[a-z]/.test(password)) score += 5;
        if (/[A-Z]/.test(password)) score += 5;
        if (/[0-9]/.test(password)) score += 5;
        if (/[^A-Za-z0-9]/.test(password)) score += 10;
        
        // Penalizar padrões comuns
        if (/(.)\1{2,}/.test(password)) score -= 10; // Repetição
        if (/123|abc|qwe/i.test(password)) score -= 10; // Sequências
        
        return Math.max(0, Math.min(100, score));
    }

    getSecurityLogs() {
        return JSON.parse(localStorage.getItem('security_logs') || '[]');
    }

    clearSecurityLogs() {
        localStorage.removeItem('security_logs');
        this.logSecurityEvent('logs_cleared');
    }
}

// Instância global
const securityManager = new SecurityManager();

// Disponibilizar globalmente para debug (apenas em desenvolvimento)
if (window.location.hostname === 'localhost') {
    window.securityManager = securityManager;
}