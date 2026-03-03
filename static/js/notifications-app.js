/**
 * Aplicación principal de gestión de notificaciones de usuario
 */

// Estado global
let allNotifications = [];
let filteredNotifications = [];
let currentFilters = {
    status: 'all',
    event: 'all',
    search: ''
};

// Elementos del DOM
let tbody, unreadBadge;
let filterStatusEl, filterEventEl, searchInputEl;
let btnRefresh, btnMarkAllRead;

/**
 * Inicialización
 */
document.addEventListener('DOMContentLoaded', async () => {
    // Obtener elementos del DOM
    tbody = document.getElementById('notifications-tbody');
    unreadBadge = document.getElementById('unread-badge');
    filterStatusEl = document.getElementById('filter-status');
    filterEventEl = document.getElementById('filter-event');
    searchInputEl = document.getElementById('search-input');
    btnRefresh = document.getElementById('btn-refresh');
    btnMarkAllRead = document.getElementById('btn-mark-all-read');

    // Configurar event listeners
    setupEventListeners();

    // Cargar notificaciones
    await loadNotifications();

    // Auto-refresh cada 30 segundos
    setInterval(() => loadNotifications(true), 30000);
});

/**
 * Configurar event listeners
 */
function setupEventListeners() {
    // Botones
    btnRefresh?.addEventListener('click', async () => {
        await loadNotifications();
        showToast('Notificaciones actualizadas', 'success');
    });
    btnMarkAllRead?.addEventListener('click', handleMarkAllAsRead);

    // Filtros
    filterStatusEl?.addEventListener('change', handleFilterChange);
    filterEventEl?.addEventListener('change', handleFilterChange);

    // Búsqueda con debounce
    let searchTimeout;
    searchInputEl?.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentFilters.search = e.target.value.toLowerCase();
            applyFilters();
        }, 300);
    });
}

/**
 * Carga las notificaciones desde la API
 */
async function loadNotifications(silent = false) {
    try {
        if (!silent) {
            showLoadingState();
        }

        const response = await NotificationsAPI.getUserNotifications();

        allNotifications = response.notifications || [];
        filteredNotifications = [...allNotifications];

        updateStats(response.total, response.unread);
        applyFilters();

        // No mostrar toast en carga inicial, solo en refresh manual
    } catch (error) {
        console.error('Error cargando notificaciones:', error);
        showError('Error al cargar las notificaciones');
    }
}

/**
 * Muestra el estado de carga
 */
function showLoadingState() {
    tbody.innerHTML = `
        <tr>
            <td colspan="6" class="loading-row">
                <div class="loading-spinner"></div>
                <span>Cargando notificaciones...</span>
            </td>
        </tr>
    `;
}

/**
 * Muestra mensaje de error
 */
function showError(message) {
    tbody.innerHTML = `
        <tr>
            <td colspan="6" style="text-align: center; padding: 2rem; color: #e74c3c;">
                <strong>⚠️ ${message}</strong>
            </td>
        </tr>
    `;
    showToast(message, 'error');
}

/**
 * Actualiza el badge del menú con notificaciones no leídas
 */
function updateStats(_total, unread) {
    // Badge en el menú lateral
    if (unread > 0) {
        unreadBadge.textContent = unread;
        unreadBadge.style.display = 'inline-block';
    } else {
        unreadBadge.style.display = 'none';
    }
}

/**
 * Maneja cambios en los filtros
 */
function handleFilterChange() {
    currentFilters.status = filterStatusEl.value;
    currentFilters.event = filterEventEl.value;
    applyFilters();
}

/**
 * Aplica los filtros a las notificaciones
 */
function applyFilters() {
    filteredNotifications = allNotifications.filter(notification => {
        // Filtro de estado
        if (currentFilters.status === 'unread' && notification.is_read) return false;
        if (currentFilters.status === 'read' && !notification.is_read) return false;

        // Filtro de evento
        if (currentFilters.event !== 'all' && notification.event_type !== currentFilters.event) {
            return false;
        }

        // Filtro de búsqueda
        if (currentFilters.search) {
            const searchLower = currentFilters.search;
            return (
                notification.solicitud_id.toLowerCase().includes(searchLower) ||
                notification.notification_subject.toLowerCase().includes(searchLower) ||
                notification.solicitud_subject.toLowerCase().includes(searchLower)
            );
        }

        return true;
    });

    renderNotifications();
}

/**
 * Renderiza la tabla de notificaciones
 */
function renderNotifications() {
    const emptyState = document.getElementById('empty-state');

    if (filteredNotifications.length === 0) {
        tbody.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';

    tbody.innerHTML = filteredNotifications.map(notification => `
        <tr class="${notification.is_read ? '' : 'unread'}" data-id="${notification.id}">
            <td>
                <span class="status-badge ${notification.is_read ? 'read' : 'unread'}">
                    <span class="icon">${notification.is_read ? '📖' : '📧'}</span>
                    ${notification.is_read ? 'Leída' : 'Nueva'}
                </span>
            </td>
            <td>
                <span class="solicitud-id">${escapeHtml(notification.solicitud_id)}</span>
            </td>
            <td>
                <span class="notification-subject">${escapeHtml(notification.notification_subject)}</span>
                <br>
                <span class="event-badge ${notification.event_type}">
                    ${formatEventType(notification.event_type)}
                </span>
            </td>
            <td>
                <span class="solicitud-subject">${escapeHtml(notification.solicitud_subject)}</span>
            </td>
            <td>
                <span class="notification-date">${formatDate(notification.created_at)}</span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn-action btn-view" onclick="handleViewSolicitud('${notification.solicitud_url || '#'}', ${notification.id}, ${notification.is_read})" title="Ver solicitud">
                        🔗 Ver
                    </button>
                    <button class="btn-action btn-delete" onclick="handleDeleteNotification(${notification.id})" title="Eliminar notificación">
                        🗑️
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

/**
 * Formatea el tipo de evento
 */
function formatEventType(eventType) {
    const labels = {
        'tramite_registrado': 'Registrado',
        'tramite_observado': 'Observado',
        'tramite_aprobado': 'Aprobado',
        'tramite_rechazado': 'Rechazado'
    };
    return labels[eventType] || eventType;
}

/**
 * Formatea una fecha
 */
function formatDate(isoString) {
    const date = new Date(isoString);
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleString('es-ES', options);
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Maneja clic en ver solicitud
 */
async function handleViewSolicitud(url, notificationId, isRead) {
    // Marcar como leída si no lo está
    if (!isRead) {
        try {
            await NotificationsAPI.markAsRead(notificationId);
            await loadNotifications(true);
        } catch (error) {
            console.error('Error marcando como leída:', error);
        }
    }

    // Navegar a la URL
    if (url && url !== '#') {
        window.open(url, '_blank');
    } else {
        showToast('No hay URL configurada para esta solicitud', 'warning');
    }
}

/**
 * Maneja eliminar notificación
 */
async function handleDeleteNotification(notificationId) {
    if (!confirm('¿Estás seguro de eliminar esta notificación?')) {
        return;
    }

    try {
        await NotificationsAPI.deleteNotification(notificationId);
        showToast('Notificación eliminada', 'success');
        await loadNotifications(true);
    } catch (error) {
        console.error('Error eliminando notificación:', error);
        showToast('Error al eliminar la notificación', 'error');
    }
}

/**
 * Marca todas como leídas
 */
async function handleMarkAllAsRead() {
    try {
        const result = await NotificationsAPI.markAllAsRead();
        showToast(result.message, 'success');
        await loadNotifications(true);
    } catch (error) {
        console.error('Error marcando todas como leídas:', error);
        showToast('Error al marcar como leídas', 'error');
    }
}

// Exponer funciones globales necesarias
window.handleViewSolicitud = handleViewSolicitud;
window.handleDeleteNotification = handleDeleteNotification;
