/**
 * Manejo de la tabla de plantillas
 */
class TemplatesTable {
    constructor(api) {
        this.api = api;
        this.templates = [];
        this.filteredTemplates = [];
        this.tbody = document.getElementById('templates-tbody');
        this.searchInput = document.getElementById('search-input');

        this.eventLabels = {
            'creacion_cuenta': 'Creación de Cuenta',
            'tramite_observado': 'Trámite Observado',
            'tramite_aprobado': 'Trámite Aprobado',
            'tramite_rechazado': 'Trámite Rechazado',
            'confirmacion_cambio_password': 'Cambio de Contraseña',
            'comprobante_pago': 'Comprobante de Pago'
        };

        this.init();
    }

    init() {
        // Event listener para búsqueda
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.filterTemplates(e.target.value);
            });
        }
    }

    async loadTemplates() {
        try {
            const data = await this.api.listTemplates();
            // Filtrar plantillas base (que empiezan con 'base_')
            this.templates = data.templates.filter(t => !t.name.startsWith('base_'));
            this.filteredTemplates = [...this.templates];
            this.render();
        } catch (error) {
            console.error('Error cargando plantillas:', error);
            this.showError('Error al cargar las plantillas');
        }
    }

    render() {
        if (!this.tbody) return;

        if (this.filteredTemplates.length === 0) {
            this.tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="no-data">
                        ${this.templates.length === 0
                            ? 'No hay plantillas. Crea una nueva para comenzar.'
                            : 'No se encontraron plantillas que coincidan con la búsqueda.'}
                    </td>
                </tr>
            `;
            return;
        }

        this.tbody.innerHTML = this.filteredTemplates.map(template => `
            <tr data-template="${template.name}">
                <td>
                    <div class="template-name-cell">
                        <strong>${this.escapeHtml(template.name)}</strong>
                        <span class="template-subject">${this.escapeHtml(template.subject || 'Sin asunto')}</span>
                    </div>
                </td>
                <td>
                    ${this.renderEventBadge(template.event_type)}
                </td>
                <td>
                    ${this.renderStatusBadge(template)}
                </td>
                <td>
                    ${this.renderActions(template)}
                </td>
            </tr>
        `).join('');

        // Adjuntar event listeners
        this.attachEventListeners();
    }

    renderEventBadge(eventType) {
        if (!eventType) {
            return '<span class="badge badge-empty">Sin evento</span>';
        }

        const label = this.eventLabels[eventType] || eventType;
        return `<span class="badge badge-event">${this.escapeHtml(label)}</span>`;
    }

    renderStatusBadge(template) {
        if (template.is_active) {
            return '<span class="badge badge-active">En uso</span>';
        }

        return `
            <button
                class="badge badge-inactive"
                data-action="activate"
                data-name="${this.escapeHtml(template.name)}"
                data-event="${this.escapeHtml(template.event_type || '')}"
                title="Click para activar esta plantilla">
                Inactiva (Click para activar)
            </button>
        `;
    }

    renderActions(template) {
        const isActive = template.is_active;

        return `
            <div class="action-buttons">
                <button
                    class="btn-action btn-edit"
                    data-action="edit"
                    data-name="${this.escapeHtml(template.name)}"
                    title="Editar plantilla">
                    ✏️ Editar
                </button>
                <button
                    class="btn-action btn-delete"
                    data-action="delete"
                    data-name="${this.escapeHtml(template.name)}"
                    ${isActive ? 'disabled' : ''}
                    title="${isActive ? 'No se puede eliminar una plantilla activa' : 'Eliminar plantilla'}">
                    🗑️ Eliminar
                </button>
            </div>
        `;
    }

    attachEventListeners() {
        if (!this.tbody) return;

        // Botones de editar
        this.tbody.querySelectorAll('[data-action="edit"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const name = e.currentTarget.dataset.name;
                if (window.templateManager) {
                    window.templateManager.openEditModal(name);
                }
            });
        });

        // Botones de eliminar
        this.tbody.querySelectorAll('[data-action="delete"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const name = e.currentTarget.dataset.name;
                if (window.templateManager) {
                    window.templateManager.deleteTemplate(name);
                }
            });
        });

        // Badges de activar
        this.tbody.querySelectorAll('[data-action="activate"]').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const templateName = e.currentTarget.dataset.name;
                const eventType = e.currentTarget.dataset.event;

                if (!eventType) {
                    if (window.templateManager) {
                        window.templateManager.showToast('Esta plantilla no tiene un evento asignado', 'error');
                    }
                    return;
                }

                if (window.templateManager) {
                    await window.templateManager.activateTemplate(eventType, templateName);
                }
            });
        });
    }

    filterTemplates(query) {
        const lowerQuery = query.toLowerCase().trim();

        if (!lowerQuery) {
            this.filteredTemplates = [...this.templates];
        } else {
            this.filteredTemplates = this.templates.filter(t =>
                t.name.toLowerCase().includes(lowerQuery) ||
                (t.subject && t.subject.toLowerCase().includes(lowerQuery)) ||
                (t.event_type && this.eventLabels[t.event_type]?.toLowerCase().includes(lowerQuery))
            );
        }

        this.render();
    }

    showError(message) {
        if (this.tbody) {
            this.tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="no-data" style="color: var(--danger-color);">
                        ⚠️ ${this.escapeHtml(message)}
                    </td>
                </tr>
            `;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
