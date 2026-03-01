/**
 * Cliente API para comunicación con el backend FastAPI
 */
class TemplateAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Error en la solicitud');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // GET /api/templates - Listar todas las plantillas
    async listTemplates() {
        return this.request('/api/templates');
    }

    // GET /api/templates/{name} - Obtener plantilla
    async getTemplate(name) {
        return this.request(`/api/templates/${encodeURIComponent(name)}`);
    }

    // POST /api/templates - Crear plantilla (con subject y event_type)
    async createTemplate(name, subject, eventType, content) {
        return this.request('/api/templates', {
            method: 'POST',
            body: JSON.stringify({
                name,
                subject,
                event_type: eventType,
                content
            })
        });
    }

    // PUT /api/templates/{name} - Actualizar plantilla (con subject, event_type y new_name opcional)
    async updateTemplate(name, subject, content, eventType = null, newName = null) {
        const body = { subject, content };
        if (eventType) {
            body.event_type = eventType;
        }
        if (newName && newName !== name) {
            body.new_name = newName;
        }
        return this.request(`/api/templates/${encodeURIComponent(name)}`, {
            method: 'PUT',
            body: JSON.stringify(body)
        });
    }

    // DELETE /api/templates/{name} - Eliminar plantilla
    async deleteTemplate(name) {
        return this.request(`/api/templates/${encodeURIComponent(name)}`, {
            method: 'DELETE'
        });
    }

    // POST /api/templates/preview - Preview de plantilla
    async previewTemplate(content, params) {
        return this.request('/api/templates/preview', {
            method: 'POST',
            body: JSON.stringify({ content, params })
        });
    }

    // POST /api/templates/validate - Validar sintaxis
    async validateTemplate(content) {
        return this.request('/api/templates/validate', {
            method: 'POST',
            body: JSON.stringify({ content })
        });
    }

    // ============================================
    // ENDPOINTS DE EVENTOS
    // ============================================

    // GET /api/events - Listar eventos con plantillas asignadas
    async listEvents() {
        return this.request('/api/events');
    }

    // PUT /api/events/{event_type}/activate - Activar plantilla para evento
    async activateTemplateForEvent(eventType, templateName) {
        return this.request(`/api/events/${encodeURIComponent(eventType)}/activate`, {
            method: 'PUT',
            body: JSON.stringify({ template_name: templateName })
        });
    }
}

// Exportar instancia
const api = new TemplateAPI();
