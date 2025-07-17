/**
 * Analisador de Design e Alinhamento
 * Biblioteca para revisar automaticamente o design e alinhamento das páginas
 */

class DesignAnalyzer {
    constructor() {
        this.issues = [];
        this.warnings = [];
        this.suggestions = [];
        this.isAnalyzing = false;
    }

    // ===============================
    // ANÁLISE PRINCIPAL
    // ===============================

    async analyzeFullPage() {
        if (this.isAnalyzing) return;
        
        this.isAnalyzing = true;
        this.clearResults();
        
        console.log('🔍 Iniciando análise completa do design...');
        
        try {
            // Executar todas as análises
            await this.analyzeLayout();
            await this.analyzeAlignment();
            await this.analyzeResponsiveness();
            await this.analyzeAccessibility();
            await this.analyzePerformance();
            
            // Gerar relatório
            this.generateReport();
            
        } catch (error) {
            console.error('Erro na análise:', error);
            this.issues.push({
                type: 'error',
                message: 'Erro durante análise: ' + error.message,
                element: null,
                severity: 'high'
            });
        } finally {
            this.isAnalyzing = false;
        }
    }

    // ===============================
    // ANÁLISE DE LAYOUT
    // ===============================

    async analyzeLayout() {
        console.log('📐 Analisando layout...');
        
        // Verificar containers principais
        const containers = document.querySelectorAll('.container, .container-fluid, .row, .col-*');
        
        containers.forEach(container => {
            const computedStyle = window.getComputedStyle(container);
            const rect = container.getBoundingClientRect();
            
            // Verificar overflow
            if (computedStyle.overflow === 'visible' && rect.width > window.innerWidth) {
                this.issues.push({
                    type: 'layout',
                    message: 'Elemento causa overflow horizontal',
                    element: container,
                    severity: 'high',
                    suggestion: 'Adicionar overflow-x: hidden ou ajustar largura'
                });
            }
            
            // Verificar altura mínima
            if (container.classList.contains('container') && rect.height < 100) {
                this.warnings.push({
                    type: 'layout',
                    message: 'Container muito baixo',
                    element: container,
                    severity: 'medium',
                    suggestion: 'Verificar se há conteúdo suficiente'
                });
            }
        });
        
        // Verificar cards
        this.analyzeCards();
        
        // Verificar grids
        this.analyzeGrids();
    }

    analyzeCards() {
        const cards = document.querySelectorAll('.card');
        
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const computedStyle = window.getComputedStyle(card);
            
            // Verificar altura dos cards em linha
            const cardRow = card.closest('.row');
            if (cardRow) {
                const siblingCards = cardRow.querySelectorAll('.card');
                if (siblingCards.length > 1) {
                    const heights = Array.from(siblingCards).map(c => c.getBoundingClientRect().height);
                    const maxHeight = Math.max(...heights);
                    const minHeight = Math.min(...heights);
                    
                    if (maxHeight - minHeight > 50) {
                        this.warnings.push({
                            type: 'alignment',
                            message: 'Cards com alturas desiguais na mesma linha',
                            element: card,
                            severity: 'medium',
                            suggestion: 'Adicionar class="h-100" nos cards'
                        });
                    }
                }
            }
            
            // Verificar alinhamento específico em cards de filtro
            const cardBody = card.querySelector('.card-body');
            if (cardBody) {
                const row = cardBody.querySelector('.row');
                if (row) {
                    const formElements = row.querySelectorAll('.form-floating, .btn, .view-toggle-container');
                    if (formElements.length > 2) {
                        const tops = Array.from(formElements).map(el => el.getBoundingClientRect().top);
                        const bottoms = Array.from(formElements).map(el => el.getBoundingClientRect().bottom);
                        
                        const maxTop = Math.max(...tops);
                        const minTop = Math.min(...tops);
                        const maxBottom = Math.max(...bottoms);
                        const minBottom = Math.min(...bottoms);
                        
                        // Verificar se elementos estão alinhados no topo OU no fundo
                        const topAligned = (maxTop - minTop) <= 5;
                        const bottomAligned = (maxBottom - minBottom) <= 5;
                        
                        if (!topAligned && !bottomAligned) {
                            this.issues.push({
                                type: 'alignment',
                                message: 'Elementos do card de filtros desalinhados',
                                element: card,
                                severity: 'high',
                                suggestion: 'Adicionar align-items-end na row ou garantir altura uniforme (58px)'
                            });
                        }
                    }
                }
            }
            
            // Verificar espaçamento
            if (parseFloat(computedStyle.marginBottom) < 16) {
                this.suggestions.push({
                    type: 'spacing',
                    message: 'Card pode precisar de mais espaçamento inferior',
                    element: card,
                    severity: 'low',
                    suggestion: 'Adicionar mb-3 ou mb-4'
                });
            }
        });
    }

    analyzeGrids() {
        const grids = document.querySelectorAll('.row');
        
        grids.forEach(grid => {
            const cols = grid.querySelectorAll('[class*="col-"]');
            
            if (cols.length > 0) {
                // Verificar alinhamento vertical
                const tops = Array.from(cols).map(col => col.getBoundingClientRect().top);
                const maxTop = Math.max(...tops);
                const minTop = Math.min(...tops);
                
                if (maxTop - minTop > 5) {
                    this.issues.push({
                        type: 'alignment',
                        message: 'Colunas desalinhadas verticalmente',
                        element: grid,
                        severity: 'high',
                        suggestion: 'Adicionar align-items-center ou align-items-end'
                    });
                }
                
                // Verificar responsividade
                const totalWidth = Array.from(cols).reduce((sum, col) => {
                    const classes = col.className.split(' ');
                    const colClass = classes.find(c => c.startsWith('col-'));
                    if (colClass) {
                        const size = parseInt(colClass.split('-').pop()) || 12;
                        return sum + size;
                    }
                    return sum + 12;
                }, 0);
                
                if (totalWidth > 12) {
                    this.warnings.push({
                        type: 'responsive',
                        message: 'Grid pode ter mais de 12 colunas',
                        element: grid,
                        severity: 'medium',
                        suggestion: 'Verificar classes das colunas'
                    });
                }
            }
        });
    }

    // ===============================
    // ANÁLISE DE ALINHAMENTO
    // ===============================

    async analyzeAlignment() {
        console.log('📏 Analisando alinhamento...');
        
        // Verificar elementos de formulário
        const formGroups = document.querySelectorAll('.form-group, .form-floating, .input-group');
        
        formGroups.forEach(group => {
            const parent = group.closest('.row');
            if (parent) {
                const siblings = parent.querySelectorAll('.form-group, .form-floating, .input-group');
                if (siblings.length > 1) {
                    const heights = Array.from(siblings).map(s => s.getBoundingClientRect().height);
                    const maxHeight = Math.max(...heights);
                    const minHeight = Math.min(...heights);
                    
                    if (maxHeight - minHeight > 10) {
                        this.issues.push({
                            type: 'alignment',
                            message: 'Elementos de formulário com alturas desiguais',
                            element: group,
                            severity: 'high',
                            suggestion: 'Usar classes de alinhamento consistentes'
                        });
                    }
                }
            }
        });
        
        // Verificar botões
        this.analyzeButtons();
        
        // Verificar textos
        this.analyzeTextAlignment();
    }

    analyzeButtons() {
        const buttonGroups = document.querySelectorAll('.btn-group, .d-flex');
        
        buttonGroups.forEach(group => {
            const buttons = group.querySelectorAll('.btn');
            if (buttons.length > 1) {
                const heights = Array.from(buttons).map(btn => btn.getBoundingClientRect().height);
                const maxHeight = Math.max(...heights);
                const minHeight = Math.min(...heights);
                
                if (maxHeight - minHeight > 5) {
                    this.warnings.push({
                        type: 'alignment',
                        message: 'Botões com alturas diferentes no mesmo grupo',
                        element: group,
                        severity: 'medium',
                        suggestion: 'Usar classes de altura consistentes'
                    });
                }
            }
        });
    }

    analyzeTextAlignment() {
        const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, div');
        
        textElements.forEach(element => {
            const computedStyle = window.getComputedStyle(element);
            const textAlign = computedStyle.textAlign;
            
            // Verificar consistência de alinhamento em grupos
            const parent = element.closest('.card-body, .form-section, .auth-card');
            if (parent) {
                const siblings = parent.querySelectorAll('h1, h2, h3, h4, h5, h6, p');
                const alignments = Array.from(siblings).map(s => window.getComputedStyle(s).textAlign);
                const uniqueAlignments = [...new Set(alignments)];
                
                if (uniqueAlignments.length > 2) {
                    this.suggestions.push({
                        type: 'consistency',
                        message: 'Múltiplos alinhamentos de texto no mesmo container',
                        element: element,
                        severity: 'low',
                        suggestion: 'Considerar padronizar alinhamento'
                    });
                }
            }
        });
    }

    // ===============================
    // ANÁLISE DE RESPONSIVIDADE
    // ===============================

    async analyzeResponsiveness() {
        console.log('📱 Analisando responsividade...');
        
        const breakpoints = [
            { name: 'mobile', width: 576 },
            { name: 'tablet', width: 768 },
            { name: 'desktop', width: 1200 }
        ];
        
        const originalWidth = window.innerWidth;
        
        for (const breakpoint of breakpoints) {
            // Simular redimensionamento
            const viewport = document.querySelector('meta[name="viewport"]');
            if (viewport) {
                // Verificar se elementos se adaptam
                const cards = document.querySelectorAll('.card');
                const grids = document.querySelectorAll('.row');
                
                // Verificar overflow em diferentes tamanhos
                cards.forEach(card => {
                    const rect = card.getBoundingClientRect();
                    if (rect.width > breakpoint.width) {
                        this.warnings.push({
                            type: 'responsive',
                            message: `Card pode não ser responsivo em ${breakpoint.name}`,
                            element: card,
                            severity: 'medium',
                            suggestion: `Adicionar classes responsivas para ${breakpoint.name}`
                        });
                    }
                });
            }
        }
    }

    // ===============================
    // ANÁLISE DE ACESSIBILIDADE
    // ===============================

    async analyzeAccessibility() {
        console.log('♿ Analisando acessibilidade...');
        
        // Verificar contraste
        const textElements = document.querySelectorAll('p, span, h1, h2, h3, h4, h5, h6, button, label');
        
        textElements.forEach(element => {
            const computedStyle = window.getComputedStyle(element);
            const color = computedStyle.color;
            const backgroundColor = computedStyle.backgroundColor;
            
            // Verificar se há contraste suficiente (simplificado)
            if (color === backgroundColor) {
                this.issues.push({
                    type: 'accessibility',
                    message: 'Texto pode ter contraste insuficiente',
                    element: element,
                    severity: 'high',
                    suggestion: 'Ajustar cores para melhor contraste'
                });
            }
        });
        
        // Verificar labels
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            const label = document.querySelector(`label[for="${input.id}"]`);
            const ariaLabel = input.getAttribute('aria-label');
            
            if (!label && !ariaLabel) {
                this.issues.push({
                    type: 'accessibility',
                    message: 'Campo sem label ou aria-label',
                    element: input,
                    severity: 'high',
                    suggestion: 'Adicionar label ou aria-label'
                });
            }
        });
    }

    // ===============================
    // ANÁLISE DE PERFORMANCE
    // ===============================

    async analyzePerformance() {
        console.log('⚡ Analisando performance...');
        
        // Verificar imagens
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            if (!img.hasAttribute('loading')) {
                this.suggestions.push({
                    type: 'performance',
                    message: 'Imagem sem lazy loading',
                    element: img,
                    severity: 'low',
                    suggestion: 'Adicionar loading="lazy"'
                });
            }
            
            if (!img.hasAttribute('alt')) {
                this.issues.push({
                    type: 'accessibility',
                    message: 'Imagem sem texto alternativo',
                    element: img,
                    severity: 'medium',
                    suggestion: 'Adicionar atributo alt'
                });
            }
        });
        
        // Verificar CSS e JS não utilizados
        const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
        const scripts = document.querySelectorAll('script[src]');
        
        if (stylesheets.length > 5) {
            this.warnings.push({
                type: 'performance',
                message: 'Muitos arquivos CSS externos',
                element: null,
                severity: 'medium',
                suggestion: 'Considerar combinar arquivos CSS'
            });
        }
        
        if (scripts.length > 10) {
            this.warnings.push({
                type: 'performance',
                message: 'Muitos scripts externos',
                element: null,
                severity: 'medium',
                suggestion: 'Considerar combinar scripts'
            });
        }
    }

    // ===============================
    // GERAÇÃO DE RELATÓRIO
    // ===============================

    generateReport() {
        console.log('📊 Gerando relatório...');
        
        const totalIssues = this.issues.length;
        const totalWarnings = this.warnings.length;
        const totalSuggestions = this.suggestions.length;
        
        // Criar elemento do relatório
        const reportElement = this.createReportElement();
        
        // Mostrar na tela
        document.body.appendChild(reportElement);
        
        // Log detalhado
        console.log(`\n🔍 RELATÓRIO DE ANÁLISE DE DESIGN:`);
        console.log(`❌ Problemas críticos: ${totalIssues}`);
        console.log(`⚠️  Avisos: ${totalWarnings}`);
        console.log(`💡 Sugestões: ${totalSuggestions}`);
        
        if (totalIssues > 0) {
            console.log(`\n❌ PROBLEMAS CRÍTICOS:`);
            this.issues.forEach((issue, index) => {
                console.log(`${index + 1}. ${issue.message}`);
                if (issue.element) {
                    console.log(`   Elemento:`, issue.element);
                }
                console.log(`   Sugestão: ${issue.suggestion}`);
            });
        }
        
        if (totalWarnings > 0) {
            console.log(`\n⚠️  AVISOS:`);
            this.warnings.forEach((warning, index) => {
                console.log(`${index + 1}. ${warning.message}`);
            });
        }
        
        return {
            issues: totalIssues,
            warnings: totalWarnings,
            suggestions: totalSuggestions,
            score: this.calculateScore()
        };
    }

    createReportElement() {
        const overlay = document.createElement('div');
        overlay.id = 'design-analyzer-report';
        overlay.innerHTML = `
            <div class="analyzer-overlay">
                <div class="analyzer-modal">
                    <div class="analyzer-header">
                        <h3>🔍 Relatório de Análise de Design</h3>
                        <button class="analyzer-close" onclick="document.getElementById('design-analyzer-report').remove()">×</button>
                    </div>
                    <div class="analyzer-content">
                        <div class="analyzer-summary">
                            <div class="score-card">
                                <div class="score-number">${this.calculateScore()}</div>
                                <div class="score-label">Score</div>
                            </div>
                            <div class="stats">
                                <div class="stat-item issues">
                                    <span class="stat-number">${this.issues.length}</span>
                                    <span class="stat-label">Problemas</span>
                                </div>
                                <div class="stat-item warnings">
                                    <span class="stat-number">${this.warnings.length}</span>
                                    <span class="stat-label">Avisos</span>
                                </div>
                                <div class="stat-item suggestions">
                                    <span class="stat-number">${this.suggestions.length}</span>
                                    <span class="stat-label">Sugestões</span>
                                </div>
                            </div>
                        </div>
                        
                        ${this.issues.length > 0 ? `
                            <div class="analyzer-section">
                                <h4>❌ Problemas Críticos</h4>
                                ${this.issues.map(issue => `
                                    <div class="issue-item ${issue.severity}">
                                        <div class="issue-message">${issue.message}</div>
                                        <div class="issue-suggestion">💡 ${issue.suggestion}</div>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                        
                        ${this.warnings.length > 0 ? `
                            <div class="analyzer-section">
                                <h4>⚠️ Avisos</h4>
                                ${this.warnings.map(warning => `
                                    <div class="issue-item ${warning.severity}">
                                        <div class="issue-message">${warning.message}</div>
                                        <div class="issue-suggestion">💡 ${warning.suggestion}</div>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                        
                        ${this.suggestions.length > 0 ? `
                            <div class="analyzer-section">
                                <h4>💡 Sugestões</h4>
                                ${this.suggestions.map(suggestion => `
                                    <div class="issue-item ${suggestion.severity}">
                                        <div class="issue-message">${suggestion.message}</div>
                                        <div class="issue-suggestion">💡 ${suggestion.suggestion}</div>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        this.addReportStyles(overlay);
        return overlay;
    }

    addReportStyles(overlay) {
        const styles = `
            .analyzer-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .analyzer-modal {
                background: white;
                border-radius: 12px;
                width: 90%;
                max-width: 800px;
                max-height: 80vh;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            }
            
            .analyzer-header {
                background: #007bff;
                color: white;
                padding: 1rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .analyzer-close {
                background: none;
                border: none;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
                padding: 0.5rem;
                border-radius: 50%;
                width: 40px;
                height: 40px;
            }
            
            .analyzer-content {
                padding: 1rem;
                max-height: 60vh;
                overflow-y: auto;
            }
            
            .analyzer-summary {
                display: flex;
                gap: 2rem;
                margin-bottom: 2rem;
                padding: 1rem;
                background: #f8f9fa;
                border-radius: 8px;
            }
            
            .score-card {
                text-align: center;
            }
            
            .score-number {
                font-size: 2rem;
                font-weight: bold;
                color: ${this.calculateScore() >= 80 ? '#28a745' : this.calculateScore() >= 60 ? '#ffc107' : '#dc3545'};
            }
            
            .stats {
                display: flex;
                gap: 1rem;
                flex: 1;
            }
            
            .stat-item {
                text-align: center;
                flex: 1;
            }
            
            .stat-number {
                display: block;
                font-size: 1.5rem;
                font-weight: bold;
            }
            
            .issues .stat-number { color: #dc3545; }
            .warnings .stat-number { color: #ffc107; }
            .suggestions .stat-number { color: #17a2b8; }
            
            .analyzer-section {
                margin-bottom: 1.5rem;
            }
            
            .issue-item {
                margin-bottom: 1rem;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #ddd;
            }
            
            .issue-item.high {
                background: #f8d7da;
                border-left-color: #dc3545;
            }
            
            .issue-item.medium {
                background: #fff3cd;
                border-left-color: #ffc107;
            }
            
            .issue-item.low {
                background: #d1ecf1;
                border-left-color: #17a2b8;
            }
            
            .issue-message {
                font-weight: bold;
                margin-bottom: 0.5rem;
            }
            
            .issue-suggestion {
                font-size: 0.9rem;
                opacity: 0.8;
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        overlay.appendChild(styleSheet);
    }

    calculateScore() {
        const totalIssues = this.issues.length;
        const totalWarnings = this.warnings.length;
        const totalSuggestions = this.suggestions.length;
        
        let score = 100;
        score -= totalIssues * 10; // -10 para cada problema crítico
        score -= totalWarnings * 5; // -5 para cada aviso
        score -= totalSuggestions * 2; // -2 para cada sugestão
        
        return Math.max(0, Math.min(100, score));
    }

    // ===============================
    // UTILITÁRIOS
    // ===============================

    clearResults() {
        this.issues = [];
        this.warnings = [];
        this.suggestions = [];
    }

    // API pública
    static analyze() {
        const analyzer = new DesignAnalyzer();
        return analyzer.analyzeFullPage();
    }
}

// Disponibilizar globalmente
window.DesignAnalyzer = DesignAnalyzer;

// Adicionar botão flutuante para análise rápida
document.addEventListener('DOMContentLoaded', function() {
    const analyzeButton = document.createElement('button');
    analyzeButton.innerHTML = '🔍 Analisar Design';
    analyzeButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 50px;
        padding: 15px 20px;
        font-size: 14px;
        cursor: pointer;
        z-index: 9999;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    `;
    
    analyzeButton.addEventListener('click', () => {
        DesignAnalyzer.analyze();
    });
    
    analyzeButton.addEventListener('mouseenter', () => {
        analyzeButton.style.transform = 'scale(1.05)';
        analyzeButton.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.4)';
    });
    
    analyzeButton.addEventListener('mouseleave', () => {
        analyzeButton.style.transform = 'scale(1)';
        analyzeButton.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';
    });
    
    document.body.appendChild(analyzeButton);
});

console.log('🔍 DesignAnalyzer carregado! Use DesignAnalyzer.analyze() ou clique no botão flutuante.');