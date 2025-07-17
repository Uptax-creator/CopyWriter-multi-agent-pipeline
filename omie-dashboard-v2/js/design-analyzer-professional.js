/**
 * Analisador de Design Profissional v2.0
 * Baseado nas principais bibliotecas e diretrizes de UI/UX:
 * - Material Design 3 (Google)
 * - Apple Human Interface Guidelines (HIG)
 * - WCAG 2.1 AA (Acessibilidade)
 * - Bootstrap 5 Design System
 * - Ant Design Guidelines
 * - Fluent UI (Microsoft)
 */

class ProfessionalDesignAnalyzer {
    constructor() {
        this.issues = [];
        this.warnings = [];
        this.suggestions = [];
        this.isAnalyzing = false;
        this.designSystems = {
            material: new MaterialDesignRules(),
            apple: new AppleHIGRules(),
            wcag: new WCAGRules(),
            bootstrap: new BootstrapRules(),
            antd: new AntDesignRules(),
            fluent: new FluentUIRules()
        };
        this.initializeRules();
    }

    initializeRules() {
        console.log('🎨 Inicializando analisador profissional com diretrizes:');
        console.log('✅ Material Design 3 (Google)');
        console.log('✅ Apple Human Interface Guidelines');
        console.log('✅ WCAG 2.1 AA (Acessibilidade)');
        console.log('✅ Bootstrap 5 Design System');
        console.log('✅ Ant Design Guidelines');
        console.log('✅ Fluent UI (Microsoft)');
    }

    // ===============================
    // ANÁLISE PRINCIPAL PROFISSIONAL
    // ===============================

    async analyzeWithProfessionalStandards() {
        if (this.isAnalyzing) return;
        
        this.isAnalyzing = true;
        this.clearResults();
        
        console.log('🔍 Iniciando análise profissional com padrões da indústria...');
        
        try {
            // Análises baseadas em padrões profissionais
            await this.analyzeMaterialDesign();
            await this.analyzeAppleHIG();
            await this.analyzeWCAGCompliance();
            await this.analyzeBootstrapPatterns();
            await this.analyzeAntDesignPatterns();
            await this.analyzeFluentUIPatterns();
            
            // Análises gerais
            await this.analyzeColorTheory();
            await this.analyzeTypography();
            await this.analyzeSpacing();
            await this.analyzeInteractionDesign();
            await this.analyzeResponsiveDesign();
            await this.analyzePerformanceUX();
            
            // Gerar relatório profissional
            this.generateProfessionalReport();
            
        } catch (error) {
            console.error('Erro na análise profissional:', error);
            this.issues.push({
                type: 'error',
                message: 'Erro durante análise profissional: ' + error.message,
                element: null,
                severity: 'high',
                designSystem: 'system'
            });
        } finally {
            this.isAnalyzing = false;
        }
    }

    // ===============================
    // ANÁLISE MATERIAL DESIGN 3
    // ===============================

    async analyzeMaterialDesign() {
        console.log('🎨 Analisando com Material Design 3...');
        
        // Verificar componentes Material
        const materialComponents = document.querySelectorAll('.btn, .card, .form-control, .alert');
        
        materialComponents.forEach(component => {
            // Verificar elevação (shadow)
            const computedStyle = window.getComputedStyle(component);
            const boxShadow = computedStyle.boxShadow;
            
            if (component.classList.contains('card') && boxShadow === 'none') {
                this.suggestions.push({
                    type: 'material-design',
                    message: 'Card sem elevação (Material Design recomenda shadow)',
                    element: component,
                    severity: 'low',
                    designSystem: 'Material Design 3',
                    suggestion: 'Adicionar box-shadow ou usar shadow classes do Bootstrap'
                });
            }
            
            // Verificar border-radius
            const borderRadius = parseFloat(computedStyle.borderRadius);
            if (borderRadius > 0 && borderRadius < 4) {
                this.warnings.push({
                    type: 'material-design',
                    message: 'Border-radius muito pequeno (Material Design recomenda 4px+)',
                    element: component,
                    severity: 'medium',
                    designSystem: 'Material Design 3',
                    suggestion: 'Usar border-radius de 4px, 8px, 12px ou 16px'
                });
            }
        });
        
        // Verificar botões Material
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            const computedStyle = window.getComputedStyle(button);
            const height = parseFloat(computedStyle.height);
            
            // Material Design recomenda altura mínima de 36px para botões
            if (height < 36) {
                this.warnings.push({
                    type: 'material-design',
                    message: 'Botão com altura menor que 36px (Material Design)',
                    element: button,
                    severity: 'medium',
                    designSystem: 'Material Design 3',
                    suggestion: 'Usar altura mínima de 36px para botões'
                });
            }
        });
    }

    // ===============================
    // ANÁLISE APPLE HIG
    // ===============================

    async analyzeAppleHIG() {
        console.log('🍎 Analisando com Apple Human Interface Guidelines...');
        
        // Verificar espaçamento baseado em 8pt grid
        const elements = document.querySelectorAll('*');
        elements.forEach(element => {
            const computedStyle = window.getComputedStyle(element);
            const marginBottom = parseFloat(computedStyle.marginBottom);
            const paddingTop = parseFloat(computedStyle.paddingTop);
            
            // Apple HIG recomenda múltiplos de 8px
            if (marginBottom > 0 && marginBottom % 8 !== 0) {
                this.suggestions.push({
                    type: 'apple-hig',
                    message: 'Espaçamento não segue 8pt grid (Apple HIG)',
                    element: element,
                    severity: 'low',
                    designSystem: 'Apple HIG',
                    suggestion: 'Usar múltiplos de 8px para espaçamentos'
                });
            }
        });
        
        // Verificar hierarquia visual
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        if (headings.length > 0) {
            const fontSizes = Array.from(headings).map(h => {
                return parseFloat(window.getComputedStyle(h).fontSize);
            });
            
            // Verificar se há progressão lógica nos tamanhos
            const sortedSizes = [...fontSizes].sort((a, b) => b - a);
            const hasLogicalProgression = fontSizes.every((size, index) => {
                return index === 0 || size <= fontSizes[index - 1];
            });
            
            if (!hasLogicalProgression) {
                this.warnings.push({
                    type: 'apple-hig',
                    message: 'Hierarquia tipográfica inconsistente (Apple HIG)',
                    element: headings[0],
                    severity: 'medium',
                    designSystem: 'Apple HIG',
                    suggestion: 'Criar progressão lógica: H1 > H2 > H3 > H4 > H5 > H6'
                });
            }
        }
    }

    // ===============================
    // ANÁLISE WCAG 2.1 AA
    // ===============================

    async analyzeWCAGCompliance() {
        console.log('♿ Analisando conformidade WCAG 2.1 AA...');
        
        // 1. Verificar contraste de cores
        const textElements = document.querySelectorAll('p, span, h1, h2, h3, h4, h5, h6, button, label, a');
        textElements.forEach(element => {
            const computedStyle = window.getComputedStyle(element);
            const color = computedStyle.color;
            const backgroundColor = computedStyle.backgroundColor;
            
            // Verificar se há contraste suficiente (implementação simplificada)
            if (this.hasLowContrast(color, backgroundColor)) {
                this.issues.push({
                    type: 'wcag-aa',
                    message: 'Contraste insuficiente (WCAG 2.1 AA)',
                    element: element,
                    severity: 'high',
                    designSystem: 'WCAG 2.1 AA',
                    suggestion: 'Usar contraste mínimo de 4.5:1 para texto normal'
                });
            }
        });
        
        // 2. Verificar foco visível
        const focusableElements = document.querySelectorAll('button, a, input, select, textarea, [tabindex]');
        focusableElements.forEach(element => {
            const computedStyle = window.getComputedStyle(element, ':focus');
            const outline = computedStyle.outline;
            const boxShadow = computedStyle.boxShadow;
            
            if (outline === 'none' && boxShadow === 'none') {
                this.issues.push({
                    type: 'wcag-aa',
                    message: 'Elemento sem indicador de foco visível (WCAG 2.1 AA)',
                    element: element,
                    severity: 'high',
                    designSystem: 'WCAG 2.1 AA',
                    suggestion: 'Adicionar outline ou box-shadow no :focus'
                });
            }
        });
        
        // 3. Verificar labels em formulários
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            const label = document.querySelector(`label[for="${input.id}"]`);
            const ariaLabel = input.getAttribute('aria-label');
            const ariaLabelledBy = input.getAttribute('aria-labelledby');
            
            if (!label && !ariaLabel && !ariaLabelledBy) {
                this.issues.push({
                    type: 'wcag-aa',
                    message: 'Campo de formulário sem label (WCAG 2.1 AA)',
                    element: input,
                    severity: 'high',
                    designSystem: 'WCAG 2.1 AA',
                    suggestion: 'Adicionar <label>, aria-label ou aria-labelledby'
                });
            }
        });
        
        // 4. Verificar imagens
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            if (!img.hasAttribute('alt')) {
                this.issues.push({
                    type: 'wcag-aa',
                    message: 'Imagem sem texto alternativo (WCAG 2.1 AA)',
                    element: img,
                    severity: 'high',
                    designSystem: 'WCAG 2.1 AA',
                    suggestion: 'Adicionar atributo alt com descrição adequada'
                });
            }
        });
    }

    // ===============================
    // ANÁLISE BOOTSTRAP 5
    // ===============================

    async analyzeBootstrapPatterns() {
        console.log('🥾 Analisando padrões Bootstrap 5...');
        
        // Verificar uso correto de classes Bootstrap
        const containers = document.querySelectorAll('.container, .container-fluid');
        containers.forEach(container => {
            const directChildren = Array.from(container.children);
            const hasRowsOnly = directChildren.every(child => child.classList.contains('row'));
            
            if (!hasRowsOnly && directChildren.length > 0) {
                this.warnings.push({
                    type: 'bootstrap',
                    message: 'Container com filhos que não são .row (Bootstrap 5)',
                    element: container,
                    severity: 'medium',
                    designSystem: 'Bootstrap 5',
                    suggestion: 'Usar .row como filhos diretos de .container'
                });
            }
        });
        
        // Verificar grid system
        const rows = document.querySelectorAll('.row');
        rows.forEach(row => {
            const columns = row.querySelectorAll('[class*="col-"]');
            let totalSize = 0;
            
            columns.forEach(col => {
                const classes = col.className.split(' ');
                const colClass = classes.find(c => c.match(/^col-\d+$/));
                if (colClass) {
                    totalSize += parseInt(colClass.split('-')[1]);
                }
            });
            
            if (totalSize > 12) {
                this.warnings.push({
                    type: 'bootstrap',
                    message: 'Grid com mais de 12 colunas (Bootstrap 5)',
                    element: row,
                    severity: 'medium',
                    designSystem: 'Bootstrap 5',
                    suggestion: 'Usar no máximo 12 colunas por .row'
                });
            }
        });
    }

    // ===============================
    // ANÁLISE ANT DESIGN
    // ===============================

    async analyzeAntDesignPatterns() {
        console.log('🐜 Analisando padrões Ant Design...');
        
        // Verificar espaçamento consistente (Ant Design usa 8px base)
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            const computedStyle = window.getComputedStyle(card);
            const padding = parseFloat(computedStyle.padding);
            
            // Ant Design recomenda padding múltiplo de 8px
            if (padding > 0 && padding % 8 !== 0) {
                this.suggestions.push({
                    type: 'ant-design',
                    message: 'Padding não segue escala 8px (Ant Design)',
                    element: card,
                    severity: 'low',
                    designSystem: 'Ant Design',
                    suggestion: 'Usar múltiplos de 8px: 8px, 16px, 24px, 32px'
                });
            }
        });
        
        // Verificar consistência de botões
        const buttons = document.querySelectorAll('.btn');
        if (buttons.length > 1) {
            const heights = Array.from(buttons).map(btn => btn.getBoundingClientRect().height);
            const uniqueHeights = [...new Set(heights)];
            
            if (uniqueHeights.length > 3) {
                this.warnings.push({
                    type: 'ant-design',
                    message: 'Muitas variações de altura de botão (Ant Design)',
                    element: buttons[0],
                    severity: 'medium',
                    designSystem: 'Ant Design',
                    suggestion: 'Usar 3 tamanhos: Small (24px), Default (32px), Large (40px)'
                });
            }
        }
    }

    // ===============================
    // ANÁLISE FLUENT UI
    // ===============================

    async analyzeFluentUIPatterns() {
        console.log('🌊 Analisando padrões Fluent UI...');
        
        // Verificar densidade de informação
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            const textContent = card.textContent.length;
            const cardArea = card.getBoundingClientRect().width * card.getBoundingClientRect().height;
            const density = textContent / cardArea * 1000;
            
            if (density > 1.5) {
                this.warnings.push({
                    type: 'fluent-ui',
                    message: 'Densidade de informação muito alta (Fluent UI)',
                    element: card,
                    severity: 'medium',
                    designSystem: 'Fluent UI',
                    suggestion: 'Reduzir densidade ou aumentar área do componente'
                });
            }
        });
        
        // Verificar hierarquia visual
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        headings.forEach(heading => {
            const computedStyle = window.getComputedStyle(heading);
            const fontWeight = computedStyle.fontWeight;
            
            if (fontWeight < 600) {
                this.suggestions.push({
                    type: 'fluent-ui',
                    message: 'Heading com peso de fonte baixo (Fluent UI)',
                    element: heading,
                    severity: 'low',
                    designSystem: 'Fluent UI',
                    suggestion: 'Usar font-weight 600+ para headings'
                });
            }
        });
    }

    // ===============================
    // ANÁLISE DE TEORIA DAS CORES
    // ===============================

    async analyzeColorTheory() {
        console.log('🎨 Analisando teoria das cores...');
        
        // Verificar paleta de cores
        const coloredElements = document.querySelectorAll('*');
        const colors = new Set();
        
        coloredElements.forEach(element => {
            const computedStyle = window.getComputedStyle(element);
            const color = computedStyle.color;
            const backgroundColor = computedStyle.backgroundColor;
            const borderColor = computedStyle.borderColor;
            
            if (color !== 'rgba(0, 0, 0, 0)') colors.add(color);
            if (backgroundColor !== 'rgba(0, 0, 0, 0)') colors.add(backgroundColor);
            if (borderColor !== 'rgba(0, 0, 0, 0)') colors.add(borderColor);
        });
        
        if (colors.size > 15) {
            this.warnings.push({
                type: 'color-theory',
                message: 'Muitas cores diferentes na paleta (>15)',
                element: document.body,
                severity: 'medium',
                designSystem: 'Color Theory',
                suggestion: 'Limitar a 8-12 cores principais + variações'
            });
        }
    }

    // ===============================
    // ANÁLISE TIPOGRÁFICA
    // ===============================

    async analyzeTypography() {
        console.log('📝 Analisando tipografia...');
        
        // Verificar escala tipográfica
        const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span');
        const fontSizes = new Set();
        
        textElements.forEach(element => {
            const fontSize = parseFloat(window.getComputedStyle(element).fontSize);
            fontSizes.add(fontSize);
        });
        
        if (fontSizes.size > 8) {
            this.warnings.push({
                type: 'typography',
                message: 'Muitos tamanhos de fonte diferentes (>8)',
                element: document.body,
                severity: 'medium',
                designSystem: 'Typography',
                suggestion: 'Usar escala tipográfica consistente (6-8 tamanhos)'
            });
        }
        
        // Verificar line-height
        const paragraphs = document.querySelectorAll('p');
        paragraphs.forEach(p => {
            const computedStyle = window.getComputedStyle(p);
            const lineHeight = parseFloat(computedStyle.lineHeight);
            const fontSize = parseFloat(computedStyle.fontSize);
            const ratio = lineHeight / fontSize;
            
            if (ratio < 1.2 || ratio > 1.8) {
                this.suggestions.push({
                    type: 'typography',
                    message: 'Line-height fora do ideal (1.2-1.8)',
                    element: p,
                    severity: 'low',
                    designSystem: 'Typography',
                    suggestion: 'Usar line-height entre 1.2-1.8x o font-size'
                });
            }
        });
    }

    // ===============================
    // UTILITÁRIOS
    // ===============================

    hasLowContrast(color1, color2) {
        // Implementação simplificada de verificação de contraste
        // Na prática, seria necessário converter para RGB e calcular o ratio
        return color1 === color2 || 
               (color1.includes('rgb(255, 255, 255)') && color2.includes('rgb(255, 255, 255)')) ||
               (color1.includes('rgb(0, 0, 0)') && color2.includes('rgb(0, 0, 0)'));
    }

    // ===============================
    // GERAÇÃO DE RELATÓRIO PROFISSIONAL
    // ===============================

    generateProfessionalReport() {
        console.log('📊 Gerando relatório profissional...');
        
        const totalIssues = this.issues.length;
        const totalWarnings = this.warnings.length;
        const totalSuggestions = this.suggestions.length;
        
        // Criar elemento do relatório profissional
        const reportElement = this.createProfessionalReportElement();
        
        // Remover relatório anterior se existir
        const existingReport = document.getElementById('professional-design-report');
        if (existingReport) {
            existingReport.remove();
        }
        
        // Mostrar na tela
        document.body.appendChild(reportElement);
        
        // Log detalhado
        console.log(`\n🔍 RELATÓRIO PROFISSIONAL DE DESIGN:`);
        console.log(`❌ Problemas críticos: ${totalIssues}`);
        console.log(`⚠️  Avisos: ${totalWarnings}`);
        console.log(`💡 Sugestões: ${totalSuggestions}`);
        console.log(`📊 Score geral: ${this.calculateProfessionalScore()}/100`);
        
        // Agrupar por design system
        const byDesignSystem = {};
        [...this.issues, ...this.warnings, ...this.suggestions].forEach(item => {
            if (!byDesignSystem[item.designSystem]) {
                byDesignSystem[item.designSystem] = [];
            }
            byDesignSystem[item.designSystem].push(item);
        });
        
        console.log('\n📋 Problemas por Design System:');
        Object.keys(byDesignSystem).forEach(system => {
            console.log(`${system}: ${byDesignSystem[system].length} itens`);
        });
        
        return {
            issues: totalIssues,
            warnings: totalWarnings,
            suggestions: totalSuggestions,
            score: this.calculateProfessionalScore(),
            byDesignSystem: byDesignSystem
        };
    }

    createProfessionalReportElement() {
        const overlay = document.createElement('div');
        overlay.id = 'professional-design-report';
        overlay.innerHTML = `
            <div class="professional-analyzer-overlay">
                <div class="professional-analyzer-modal">
                    <div class="professional-analyzer-header">
                        <h3>🎨 Relatório Profissional de Design</h3>
                        <button class="analyzer-close" onclick="document.getElementById('professional-design-report').remove()">×</button>
                    </div>
                    <div class="professional-analyzer-content">
                        <div class="professional-analyzer-summary">
                            <div class="score-card-professional">
                                <div class="score-number-professional">${this.calculateProfessionalScore()}</div>
                                <div class="score-label">Score Profissional</div>
                                <div class="score-grade">${this.getGrade()}</div>
                            </div>
                            <div class="design-systems-overview">
                                <h4>Design Systems Analisados:</h4>
                                <div class="systems-grid">
                                    <div class="system-item">🎨 Material Design 3</div>
                                    <div class="system-item">🍎 Apple HIG</div>
                                    <div class="system-item">♿ WCAG 2.1 AA</div>
                                    <div class="system-item">🥾 Bootstrap 5</div>
                                    <div class="system-item">🐜 Ant Design</div>
                                    <div class="system-item">🌊 Fluent UI</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="professional-stats">
                            <div class="stat-item-professional issues">
                                <span class="stat-number">${this.issues.length}</span>
                                <span class="stat-label">Problemas Críticos</span>
                            </div>
                            <div class="stat-item-professional warnings">
                                <span class="stat-number">${this.warnings.length}</span>
                                <span class="stat-label">Avisos</span>
                            </div>
                            <div class="stat-item-professional suggestions">
                                <span class="stat-number">${this.suggestions.length}</span>
                                <span class="stat-label">Sugestões</span>
                            </div>
                        </div>
                        
                        ${this.renderDesignSystemSections()}
                    </div>
                </div>
            </div>
        `;
        
        this.addProfessionalReportStyles(overlay);
        return overlay;
    }

    renderDesignSystemSections() {
        const sections = [];
        
        // Agrupar por design system
        const byDesignSystem = {};
        [...this.issues, ...this.warnings, ...this.suggestions].forEach(item => {
            if (!byDesignSystem[item.designSystem]) {
                byDesignSystem[item.designSystem] = [];
            }
            byDesignSystem[item.designSystem].push(item);
        });
        
        Object.keys(byDesignSystem).forEach(system => {
            const items = byDesignSystem[system];
            const systemIcon = this.getSystemIcon(system);
            
            sections.push(`
                <div class="design-system-section">
                    <h4>${systemIcon} ${system}</h4>
                    <div class="system-items">
                        ${items.map(item => `
                            <div class="system-item-detail ${item.severity}">
                                <div class="item-type">${item.type}</div>
                                <div class="item-message">${item.message}</div>
                                <div class="item-suggestion">💡 ${item.suggestion}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `);
        });
        
        return sections.join('');
    }

    getSystemIcon(system) {
        const icons = {
            'Material Design 3': '🎨',
            'Apple HIG': '🍎',
            'WCAG 2.1 AA': '♿',
            'Bootstrap 5': '🥾',
            'Ant Design': '🐜',
            'Fluent UI': '🌊',
            'Color Theory': '🌈',
            'Typography': '📝'
        };
        return icons[system] || '📐';
    }

    addProfessionalReportStyles(overlay) {
        const styles = `
            .professional-analyzer-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.9);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .professional-analyzer-modal {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 20px;
                width: 95%;
                max-width: 1000px;
                max-height: 90vh;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
                color: white;
            }
            
            .professional-analyzer-header {
                background: rgba(0, 0, 0, 0.3);
                padding: 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                backdrop-filter: blur(10px);
            }
            
            .professional-analyzer-header h3 {
                margin: 0;
                font-size: 1.8rem;
                font-weight: 700;
            }
            
            .professional-analyzer-content {
                padding: 2rem;
                max-height: 70vh;
                overflow-y: auto;
                background: rgba(255, 255, 255, 0.95);
                color: #333;
            }
            
            .professional-analyzer-summary {
                display: flex;
                gap: 2rem;
                margin-bottom: 2rem;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            
            .score-card-professional {
                text-align: center;
                min-width: 150px;
            }
            
            .score-number-professional {
                font-size: 3rem;
                font-weight: 800;
                color: ${this.calculateProfessionalScore() >= 80 ? '#28a745' : this.calculateProfessionalScore() >= 60 ? '#ffc107' : '#dc3545'};
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .score-grade {
                font-size: 1.2rem;
                font-weight: 600;
                margin-top: 0.5rem;
                color: #666;
            }
            
            .design-systems-overview {
                flex: 1;
            }
            
            .systems-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 0.5rem;
                margin-top: 1rem;
            }
            
            .system-item {
                background: rgba(255, 255, 255, 0.2);
                padding: 0.5rem;
                border-radius: 8px;
                text-align: center;
                font-size: 0.9rem;
                font-weight: 500;
            }
            
            .professional-stats {
                display: flex;
                justify-content: center;
                gap: 3rem;
                margin-bottom: 2rem;
                padding: 1.5rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
            
            .stat-item-professional {
                text-align: center;
            }
            
            .stat-item-professional .stat-number {
                display: block;
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
            }
            
            .stat-item-professional.issues .stat-number { color: #dc3545; }
            .stat-item-professional.warnings .stat-number { color: #ffc107; }
            .stat-item-professional.suggestions .stat-number { color: #17a2b8; }
            
            .design-system-section {
                margin-bottom: 2rem;
                padding: 1.5rem;
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.1);
            }
            
            .design-system-section h4 {
                margin-bottom: 1rem;
                color: #333;
                font-weight: 600;
            }
            
            .system-item-detail {
                margin-bottom: 1rem;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #ddd;
            }
            
            .system-item-detail.high {
                background: rgba(248, 215, 218, 0.8);
                border-left-color: #dc3545;
            }
            
            .system-item-detail.medium {
                background: rgba(255, 243, 205, 0.8);
                border-left-color: #ffc107;
            }
            
            .system-item-detail.low {
                background: rgba(209, 236, 241, 0.8);
                border-left-color: #17a2b8;
            }
            
            .item-type {
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
                color: #666;
                margin-bottom: 0.25rem;
            }
            
            .item-message {
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: #333;
            }
            
            .item-suggestion {
                font-size: 0.9rem;
                color: #666;
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        overlay.appendChild(styleSheet);
    }

    calculateProfessionalScore() {
        const totalIssues = this.issues.length;
        const totalWarnings = this.warnings.length;
        const totalSuggestions = this.suggestions.length;
        
        let score = 100;
        score -= totalIssues * 15; // -15 para cada problema crítico
        score -= totalWarnings * 8; // -8 para cada aviso
        score -= totalSuggestions * 3; // -3 para cada sugestão
        
        return Math.max(0, Math.min(100, score));
    }

    getGrade() {
        const score = this.calculateProfessionalScore();
        if (score >= 90) return 'A+';
        if (score >= 80) return 'A';
        if (score >= 70) return 'B';
        if (score >= 60) return 'C';
        if (score >= 50) return 'D';
        return 'F';
    }

    clearResults() {
        this.issues = [];
        this.warnings = [];
        this.suggestions = [];
    }

    // API pública
    static analyze() {
        const analyzer = new ProfessionalDesignAnalyzer();
        return analyzer.analyzeWithProfessionalStandards();
    }
}

// Classes auxiliares para regras específicas
class MaterialDesignRules {
    constructor() {
        this.name = 'Material Design 3';
        this.version = '3.0';
    }
}

class AppleHIGRules {
    constructor() {
        this.name = 'Apple Human Interface Guidelines';
        this.version = '2024';
    }
}

class WCAGRules {
    constructor() {
        this.name = 'WCAG 2.1 AA';
        this.version = '2.1';
    }
}

class BootstrapRules {
    constructor() {
        this.name = 'Bootstrap 5';
        this.version = '5.3';
    }
}

class AntDesignRules {
    constructor() {
        this.name = 'Ant Design';
        this.version = '5.0';
    }
}

class FluentUIRules {
    constructor() {
        this.name = 'Fluent UI';
        this.version = '9.0';
    }
}

// Disponibilizar globalmente
window.ProfessionalDesignAnalyzer = ProfessionalDesignAnalyzer;

// Adicionar botão flutuante profissional
document.addEventListener('DOMContentLoaded', function() {
    const analyzeButton = document.createElement('button');
    analyzeButton.innerHTML = '🎨 Análise Profissional';
    analyzeButton.style.cssText = `
        position: fixed;
        bottom: 80px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 15px 20px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        z-index: 9998;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    `;
    
    analyzeButton.addEventListener('click', () => {
        ProfessionalDesignAnalyzer.analyze();
    });
    
    analyzeButton.addEventListener('mouseenter', () => {
        analyzeButton.style.transform = 'scale(1.05)';
        analyzeButton.style.boxShadow = '0 6px 24px rgba(102, 126, 234, 0.6)';
    });
    
    analyzeButton.addEventListener('mouseleave', () => {
        analyzeButton.style.transform = 'scale(1)';
        analyzeButton.style.boxShadow = '0 4px 20px rgba(102, 126, 234, 0.4)';
    });
    
    document.body.appendChild(analyzeButton);
});

console.log('🎨 ProfessionalDesignAnalyzer carregado! Baseado em Material Design 3, Apple HIG, WCAG 2.1 AA, Bootstrap 5, Ant Design e Fluent UI.');