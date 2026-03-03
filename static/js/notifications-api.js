/**
 * API Client para notificaciones internas
 */

const API_BASE = '';
const USER_ID = 'user_demo'; // En producción, esto vendría de la sesión del usuario

class NotificationsAPI {
    /**
     * Obtiene las notificaciones del usuario
     * @param {Object} options - Opciones de filtrado
     * @param {number} options.limit - Límite de resultados
     * @param {boolean} options.only_unread - Solo no leídas
     * @returns {Promise<Object>} Response con notificaciones
     */
    static async getUserNotifications(options = {}) {
        const params = new URLSearchParams();
        if (options.limit) params.append('limit', options.limit);
        if (options.only_unread) params.append('only_unread', 'true');

        const url = `${API_BASE}/api/internal-notifications/user/${USER_ID}${params.toString() ? '?' + params.toString() : ''}`;

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    /**
     * Crea una nueva notificación interna
     * @param {Object} notification - Datos de la notificación
     * @returns {Promise<Object>} Notificación creada
     */
    static async createNotification(notification) {
        const response = await fetch(`${API_BASE}/api/internal-notifications`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(notification)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error creating notification');
        }

        return await response.json();
    }

    /**
     * Marca una notificación como leída
     * @param {number} notificationId - ID de la notificación
     * @returns {Promise<Object>} Response
     */
    static async markAsRead(notificationId) {
        const response = await fetch(`${API_BASE}/api/internal-notifications/${notificationId}/read`, {
            method: 'PUT'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Marca todas las notificaciones como leídas
     * @returns {Promise<Object>} Response
     */
    static async markAllAsRead() {
        const response = await fetch(`${API_BASE}/api/internal-notifications/user/${USER_ID}/read-all`, {
            method: 'PUT'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Obtiene el contador de no leídas
     * @returns {Promise<Object>} {unread_count: number}
     */
    static async getUnreadCount() {
        const response = await fetch(`${API_BASE}/api/internal-notifications/user/${USER_ID}/unread-count`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Elimina una notificación
     * @param {number} notificationId - ID de la notificación
     * @returns {Promise<Object>} Response
     */
    static async deleteNotification(notificationId) {
        const response = await fetch(`${API_BASE}/api/internal-notifications/${notificationId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Obtiene resumen de notificaciones
     * @returns {Promise<Object>} {total, unread, recent}
     */
    static async getSummary() {
        const response = await fetch(`${API_BASE}/api/internal-notifications/user/${USER_ID}/summary`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }
}

/**
 * Helper para mostrar mensajes toast
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = {
        'success': '✓',
        'error': '✗',
        'info': 'ℹ',
        'warning': '⚠'
    }[type] || 'ℹ';

    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    // Animación de entrada
    setTimeout(() => toast.classList.add('show'), 100);

    // Remover después de 3 segundos
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
