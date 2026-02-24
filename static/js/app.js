/**
 * Aplicación principal de gestión de plantillas WYSIWYG
 */
class TemplateManager {
    constructor() {
        this.api = api;
        this.editor = null;
        this.currentTemplate = null;
        this.templates = [];
        this.hasUnsavedChanges = false;

        // Valores por defecto para variables
        this.defaultValues = {
            'name': 'Fabián García',
            'email': 'fabian@ejemplo.com',
            'phone': '+1234567890',
            'company': 'Campus 360',
            'date': new Date().toLocaleDateString(),
            'link': 'https://ejemplo.com',
            'code': '123456',
            'message': 'Este es un mensaje de ejemplo'
        };

        this.init();
    }

    async init() {
        // Inicializar editor
        this.editor = new TemplateEditor('editor');

        // Configurar event listeners
        this.setupEventListeners();

        // Cargar plantillas
        await this.loadTemplates();
    }

    setupEventListeners() {
        // Botones principales
        document.getElementById('btn-new').addEventListener('click', () => this.showNewTemplateModal());
        document.getElementById('btn-save').addEventListener('click', () => this.saveTemplate());
        document.getElementById('btn-delete').addEventListener('click', () => this.deleteTemplate());
        document.getElementById('btn-refresh-preview').addEventListener('click', () => this.updatePreview());

        // Modal
        document.querySelector('.modal-close').addEventListener('click', () => this.hideNewTemplateModal());
        document.getElementById('btn-modal-cancel').addEventListener('click', () => this.hideNewTemplateModal());
        document.getElementById('btn-modal-create').addEventListener('click', () => this.createTemplate());

        // Enter en input de nombre para crear
        document.getElementById('new-template-name').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.createTemplate();
            }
        });

        // NUEVO: Event listeners para botones de variables
        document.querySelectorAll('.var-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const variable = btn.dataset.var;
                this.editor.insertVariable(variable);
                this.hasUnsavedChanges = true;

                // Actualizar preview automáticamente
                if (this.currentTemplate) {
                    this.updatePreview();
                }
            });
        });

        // Editor changes
        this.editor.onChange((content) => this.onEditorChange(content));

        // Prevenir salir sin guardar
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    }

    async loadTemplates() {
        try {
            const data = await this.api.listTemplates();
            // Filtrar plantillas base (no mostrar en la lista lateral)
            this.templates = data.templates.filter(name =>
                !name.startsWith('base_')
            );
            this.renderTemplateList();
        } catch (error) {
            this.showToast('Error cargando plantillas', 'error');
            console.error(error);
        }
    }

    renderTemplateList() {
        const listContainer = document.getElementById('template-list');

        if (this.templates.length === 0) {
            listContainer.innerHTML = '<div class="loading">No hay plantillas. Crea una nueva.</div>';
            return;
        }

        listContainer.innerHTML = this.templates.map(name => `
            <div class="template-item" data-template="${name}">
                <span class="template-item-name">${name}</span>
            </div>
        `).join('');

        // Event listeners para items
        listContainer.querySelectorAll('.template-item').forEach(item => {
            item.addEventListener('click', () => {
                const name = item.dataset.template;
                this.loadTemplate(name);
            });
        });
    }

    async loadTemplate(name) {
        // Verificar cambios sin guardar
        if (this.hasUnsavedChanges) {
            if (!confirm('Tienes cambios sin guardar. ¿Deseas continuar?')) {
                return;
            }
        }

        try {
            const template = await this.api.getTemplate(name);

            this.currentTemplate = template;
            this.editor.setValue(template.content);
            this.hasUnsavedChanges = false;

            // Actualizar UI
            document.getElementById('current-template-name').textContent = template.name;
            document.getElementById('file-info').textContent =
                `Tamaño: ${template.size} bytes | Modificado: ${new Date(template.modified).toLocaleString()}`;

            document.getElementById('btn-save').disabled = false;
            document.getElementById('btn-delete').disabled = false;

            // Marcar como activo en lista
            document.querySelectorAll('.template-item').forEach(item => {
                item.classList.toggle('active', item.dataset.template === name);
            });

            // Actualizar preview automáticamente
            this.updatePreview();

        } catch (error) {
            this.showToast(`Error cargando plantilla: ${error.message}`, 'error');
        }
    }

    showNewTemplateModal() {
        document.getElementById('modal-new-template').classList.add('show');
        document.getElementById('new-template-name').value = '';
        document.getElementById('base-template-selector').value = '';
        document.getElementById('new-template-name').focus();
    }

    hideNewTemplateModal() {
        document.getElementById('modal-new-template').classList.remove('show');
    }

    async createTemplate() {
        const nameInput = document.getElementById('new-template-name');
        const baseSelector = document.getElementById('base-template-selector');

        const name = nameInput.value.trim();
        const baseTemplate = baseSelector.value;

        if (!name) {
            this.showToast('El nombre es requerido', 'error');
            return;
        }

        let content = '<p>Nueva plantilla - comienza a escribir...</p>';

        try {
            // Si seleccionó una plantilla base, cargar su contenido
            if (baseTemplate) {
                console.log('Cargando plantilla base:', baseTemplate);
                const baseData = await this.api.getTemplate(baseTemplate);
                console.log('Contenido cargado:', baseData.content.substring(0, 100) + '...');
                content = baseData.content;
            }

            console.log('Creando plantilla con contenido:', content.substring(0, 100) + '...');

            // Crear la nueva plantilla
            await this.api.createTemplate(name, content);

            this.hideNewTemplateModal();
            this.showToast('Plantilla creada correctamente', 'success');

            // Recargar lista
            await this.loadTemplates();

            // Cargar nueva plantilla
            await this.loadTemplate(name);

        } catch (error) {
            console.error('Error completo:', error);
            this.showToast(`Error creando plantilla: ${error.message}`, 'error');
        }
    }

    async saveTemplate() {
        if (!this.currentTemplate) return;

        const content = this.editor.getValue();

        if (!content || content.trim() === '') {
            this.showToast('La plantilla no puede estar vacía', 'error');
            return;
        }

        try {
            await this.api.updateTemplate(this.currentTemplate.name, content);

            this.hasUnsavedChanges = false;
            this.currentTemplate.content = content;

            this.showToast('Plantilla guardada correctamente', 'success');

            // Actualizar validación
            this.validateContent(content);

        } catch (error) {
            this.showToast(`Error guardando plantilla: ${error.message}`, 'error');
        }
    }

    async deleteTemplate() {
        if (!this.currentTemplate) return;

        if (!confirm(`¿Estás seguro de eliminar la plantilla "${this.currentTemplate.name}"?\n\nEsta acción no se puede deshacer.`)) {
            return;
        }

        try {
            await this.api.deleteTemplate(this.currentTemplate.name);

            this.showToast('Plantilla eliminada correctamente', 'success');

            // Limpiar editor
            this.currentTemplate = null;
            this.editor.clear();
            this.hasUnsavedChanges = false;

            document.getElementById('current-template-name').textContent = 'Selecciona una plantilla';
            document.getElementById('file-info').textContent = '';
            document.getElementById('btn-save').disabled = true;
            document.getElementById('btn-delete').disabled = true;

            // Recargar lista
            await this.loadTemplates();

            // Limpiar preview
            this.clearPreview();

        } catch (error) {
            this.showToast(`Error eliminando plantilla: ${error.message}`, 'error');
        }
    }

    async onEditorChange(content) {
        if (this.currentTemplate) {
            this.hasUnsavedChanges = true;

            // Validar sintaxis en tiempo real (debounced)
            clearTimeout(this.validateTimeout);
            this.validateTimeout = setTimeout(() => {
                this.validateContent(content);
                // También actualizar preview automáticamente
                this.updatePreview();
            }, 1000);
        }
    }

    async validateContent(content) {
        try {
            const result = await this.api.validateTemplate(content);

            const statusBadge = document.getElementById('template-status');
            const validationStatus = document.getElementById('validation-status');

            if (result.valid) {
                statusBadge.textContent = '✓ Válido';
                statusBadge.className = 'status-badge valid';
                validationStatus.textContent = 'Plantilla válida';
                validationStatus.className = 'validation-status';
            } else {
                statusBadge.textContent = '✗ Error';
                statusBadge.className = 'status-badge invalid';
                validationStatus.textContent = `Error: ${result.error}`;
                validationStatus.className = 'validation-status error';
            }

        } catch (error) {
            console.error('Error validando:', error);
        }
    }

    async updatePreview() {
        if (!this.currentTemplate) return;

        const content = this.editor.getValue();

        // Extraer variables usadas en la plantilla
        const usedVars = this.extractVariables(content);

        // Generar parámetros automáticamente
        const params = {};
        usedVars.forEach(varName => {
            params[varName] = this.getDefaultValue(varName);
        });

        // Mostrar variables detectadas
        this.showDetectedVariables(usedVars, params);

        try {
            const result = await this.api.previewTemplate(content, params);

            const previewContent = document.getElementById('preview-content');

            if (result.valid) {
                previewContent.innerHTML = result.rendered;
            } else {
                this.showPreviewError(result.error);
            }

        } catch (error) {
            this.showPreviewError(error.message);
        }
    }

    /**
     * Extraer variables Handlebars de la plantilla
     */
    extractVariables(content) {
        const regex = /\{\{([a-zA-Z_]+)\}\}/g;
        const vars = new Set();
        let match;

        while ((match = regex.exec(content)) !== null) {
            vars.add(match[1]);
        }

        return Array.from(vars);
    }

    /**
     * Obtener valor por defecto para una variable
     */
    getDefaultValue(varName) {
        return this.defaultValues[varName] || `{${varName}}`;
    }

    /**
     * Mostrar variables detectadas en el panel de preview
     */
    showDetectedVariables(vars, params) {
        const container = document.getElementById('detected-vars');

        if (vars.length === 0) {
            container.innerHTML = '<p class="no-vars">No se detectaron variables en la plantilla</p>';
            return;
        }

        container.innerHTML = vars.map(varName => `
            <div class="var-preview-item">
                <span class="var-preview-name">{{${varName}}}</span>
                <span class="var-preview-value">${params[varName]}</span>
            </div>
        `).join('');
    }

    showPreviewError(message) {
        const previewContent = document.getElementById('preview-content');
        previewContent.innerHTML = `
            <div class="preview-error">
                <strong>Error en el preview:</strong><br>
                ${message}
            </div>
        `;
    }

    clearPreview() {
        const previewContent = document.getElementById('preview-content');
        previewContent.innerHTML = '<div class="preview-placeholder">Selecciona una plantilla para ver el preview</div>';

        const container = document.getElementById('detected-vars');
        container.innerHTML = '';
    }

    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Inicializar aplicación
document.addEventListener('DOMContentLoaded', () => {
    new TemplateManager();
});
