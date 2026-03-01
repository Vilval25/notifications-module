/**
 * Aplicación principal de gestión de plantillas
 * Refactorizada para usar tabla y eliminar preview
 */
class TemplateManager {
    constructor() {
        this.api = api;
        this.editor = null;
        this.table = null;
        this.sidebar = null;
        this.currentTemplate = null;
        this.isEditMode = false;

        this.init();
    }

    async init() {
        console.log('Inicializando Template Manager...');

        // Inicializar componentes
        this.sidebar = new Sidebar();
        this.table = new TemplatesTable(this.api);
        // El editor se inicializará cuando se abra el modal por primera vez

        // Configurar event listeners
        this.setupEventListeners();

        // Cargar plantillas
        await this.table.loadTemplates();

        console.log('Template Manager inicializado correctamente');
    }

    setupEventListeners() {
        // Botón nueva plantilla
        const btnNew = document.getElementById('btn-new');
        if (btnNew) {
            btnNew.addEventListener('click', () => this.openNewModal());
        }

        // Modal - botones
        const modalCloseBtn = document.getElementById('modal-close-btn');
        const btnModalCancel = document.getElementById('btn-modal-cancel');
        const btnModalSave = document.getElementById('btn-modal-save');

        if (modalCloseBtn) {
            modalCloseBtn.addEventListener('click', () => this.closeModal());
        }
        if (btnModalCancel) {
            btnModalCancel.addEventListener('click', () => this.closeModal());
        }
        if (btnModalSave) {
            btnModalSave.addEventListener('click', () => this.saveTemplate());
        }

        // Variable selector - insertar variables en el editor
        const variableSelector = document.getElementById('variable-selector');
        if (variableSelector) {
            variableSelector.addEventListener('change', (e) => {
                if (e.target.value && this.editor) {
                    this.editor.insertVariable(e.target.value);
                    e.target.value = ''; // Reset selector
                }
            });
        }

        // Cerrar modal al hacer click fuera
        const modal = document.getElementById('modal-editor');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        }
    }

    openNewModal() {
        this.isEditMode = false;
        this.currentTemplate = null;

        // Inicializar editor si no existe
        if (!this.editor) {
            this.editor = new TemplateEditor('editor');
        }

        // Actualizar título
        const modalTitle = document.getElementById('modal-title');
        if (modalTitle) {
            modalTitle.textContent = 'Nueva Plantilla';
        }

        // Limpiar y habilitar campos
        const inputName = document.getElementById('input-name');
        const inputEvent = document.getElementById('input-event');
        const inputSubject = document.getElementById('input-subject');

        if (inputName) {
            inputName.value = '';
            inputName.disabled = false;
        }
        if (inputEvent) {
            inputEvent.value = '';
            inputEvent.disabled = false;

            // Resetear mensaje de ayuda
            const eventHelp = inputEvent.parentElement.querySelector('.form-help');
            if (eventHelp) {
                eventHelp.textContent = 'El evento solo se puede cambiar si la plantilla no está en uso';
                eventHelp.style.color = '';
            }
        }
        if (inputSubject) {
            inputSubject.value = '';
        }

        // Limpiar editor
        this.editor.clear();

        // Mostrar modal
        const modal = document.getElementById('modal-editor');
        if (modal) {
            modal.classList.add('show');
        }
    }

    async openEditModal(name) {
        try {
            // Cargar plantilla
            const template = await this.api.getTemplate(name);

            this.isEditMode = true;
            this.currentTemplate = template;

            // Inicializar editor si no existe
            if (!this.editor) {
                this.editor = new TemplateEditor('editor');
            }

            // Actualizar título
            const modalTitle = document.getElementById('modal-title');
            if (modalTitle) {
                modalTitle.textContent = `Editar: ${name}`;
            }

            // Llenar campos
            const inputName = document.getElementById('input-name');
            const inputEvent = document.getElementById('input-event');
            const inputSubject = document.getElementById('input-subject');

            if (inputName) {
                inputName.value = template.name;
                inputName.disabled = false; // Ahora se puede cambiar el nombre
            }
            if (inputEvent) {
                inputEvent.value = template.event_type || '';
                // Solo permitir cambiar evento si la plantilla NO está activa
                inputEvent.disabled = template.is_active;

                // Mostrar mensaje informativo si está activa
                const eventHelp = inputEvent.parentElement.querySelector('.form-help');
                if (eventHelp) {
                    if (template.is_active) {
                        eventHelp.textContent = 'No se puede cambiar el evento mientras la plantilla esté activa';
                        eventHelp.style.color = 'var(--warning-color)';
                    } else {
                        eventHelp.textContent = 'Puede cambiar el evento porque esta plantilla no está en uso';
                        eventHelp.style.color = 'var(--success-color)';
                    }
                }
            }
            if (inputSubject) {
                inputSubject.value = template.subject || '';
            }

            // Cargar contenido en editor
            this.editor.setValue(template.content);

            // Mostrar modal
            const modal = document.getElementById('modal-editor');
            if (modal) {
                modal.classList.add('show');
            }
        } catch (error) {
            this.showToast(`Error cargando plantilla: ${error.message}`, 'error');
            console.error(error);
        }
    }

    closeModal() {
        const modal = document.getElementById('modal-editor');
        if (modal) {
            modal.classList.remove('show');
        }
    }

    async saveTemplate() {
        // Verificar que el editor esté inicializado
        if (!this.editor) {
            this.showToast('Error: Editor no inicializado', 'error');
            return;
        }

        // Obtener valores del formulario
        const name = document.getElementById('input-name')?.value.trim();
        const eventType = document.getElementById('input-event')?.value;
        const subject = document.getElementById('input-subject')?.value.trim();
        const content = this.editor.getValue();

        console.log('Guardando plantilla:', { name, eventType, subject, isEditMode: this.isEditMode });

        // Validaciones
        if (!name) {
            this.showToast('El nombre de la plantilla es obligatorio', 'error');
            return;
        }

        if (!subject) {
            this.showToast('El asunto es obligatorio', 'error');
            return;
        }

        if (!content || content.trim() === '<p><br></p>' || content.trim() === '') {
            this.showToast('El cuerpo de la plantilla no puede estar vacío', 'error');
            return;
        }

        if (!this.isEditMode && !eventType) {
            this.showToast('Debes seleccionar un evento', 'error');
            return;
        }

        try {
            if (this.isEditMode) {
                // Actualizar plantilla existente
                const originalName = this.currentTemplate?.name;
                const originalEventType = this.currentTemplate?.event_type;

                // Verificar si el evento cambió
                const newEventType = (eventType && eventType !== originalEventType) ? eventType : null;

                // Verificar si el nombre cambió
                const newName = (name !== originalName) ? name : null;

                await this.api.updateTemplate(originalName, subject, content, newEventType, newName);
                this.showToast('Plantilla actualizada correctamente', 'success');
            } else {
                // Crear nueva plantilla
                await this.api.createTemplate(name, subject, eventType, content);
                this.showToast('Plantilla creada correctamente', 'success');
            }

            // Cerrar modal
            this.closeModal();

            // Recargar tabla
            await this.table.loadTemplates();

        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
            console.error(error);
        }
    }

    async activateTemplate(eventType, templateName) {
        // Confirmar antes de activar
        if (!confirm(`¿Activar la plantilla "${templateName}" para el evento "${eventType}"?\n\nLa plantilla anterior se desactivará automáticamente.`)) {
            return;
        }

        try {
            await this.api.activateTemplateForEvent(eventType, templateName);
            this.showToast('Plantilla activada correctamente', 'success');

            // Recargar tabla para reflejar cambios
            await this.table.loadTemplates();

        } catch (error) {
            this.showToast(`Error activando plantilla: ${error.message}`, 'error');
            console.error(error);
        }
    }

    async deleteTemplate(name) {
        // Confirmar antes de eliminar
        if (!confirm(`¿Estás seguro de eliminar la plantilla "${name}"?\n\nEsta acción no se puede deshacer.`)) {
            return;
        }

        try {
            await this.api.deleteTemplate(name);
            this.showToast('Plantilla eliminada correctamente', 'success');

            // Recargar tabla
            await this.table.loadTemplates();

        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
            console.error(error);
        }
    }

    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        // Auto-remover después de 3 segundos
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Exponer globalmente para que table.js pueda acceder
window.templateManager = null;

// Inicializar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.templateManager = new TemplateManager();
});
