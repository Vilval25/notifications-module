/**
 * Gestor de Suscripciones
 * Maneja la interfaz de usuario para las preferencias de notificación
 */

// Configuración
const SUBSCRIPTION_USER_ID = 'user_demo'; // En producción, obtener del sistema de autenticación

// Etiquetas de eventos
const EVENT_LABELS = {
    'tramite_registrado': {
        label: 'Trámite Registrado',
        icon: '📝',
        description: 'Cuando se registra un nuevo trámite'
    },
    'tramite_observado': {
        label: 'Trámite con Observaciones',
        icon: '⚠️',
        description: 'Cuando tu trámite tiene observaciones'
    },
    'tramite_aprobado': {
        label: 'Trámite Aprobado',
        icon: '✅',
        description: 'Cuando tu trámite es aprobado'
    },
    'tramite_rechazado': {
        label: 'Trámite Rechazado',
        icon: '❌',
        description: 'Cuando tu trámite es rechazado'
    }
};

// Etiquetas de canales
const CHANNEL_LABELS = {
    'email': '📧 Correo',
    'sms': '📱 SMS',
    'whatsapp': '💬 WhatsApp'
};

// Estado de las suscripciones
let currentSubscriptions = [];
let hasChanges = false;

/**
 * Inicializa el gestor de suscripciones
 */
async function initSubscriptionsManager() {
    await loadSubscriptions();
    setupSubscriptionListeners();
}

/**
 * Carga las suscripciones del usuario
 */
async function loadSubscriptions() {
    const contentEl = document.getElementById('subscriptions-content');
    const saveBtn = document.getElementById('btn-save-subscriptions');

    try {
        const response = await SubscriptionsAPI.getUserSubscriptions(SUBSCRIPTION_USER_ID);
        currentSubscriptions = response.subscriptions;

        // Renderizar suscripciones
        renderSubscriptions(currentSubscriptions);

        // Ocultar botón de guardar inicialmente
        saveBtn.style.display = 'none';
        hasChanges = false;
    } catch (error) {
        contentEl.innerHTML = `
            <div class="error-message">
                <p>❌ Error al cargar las preferencias de notificación</p>
                <p style="font-size: 0.9rem; color: #7f8c8d;">${error.message}</p>
            </div>
        `;
    }
}

/**
 * Renderiza las suscripciones en la interfaz
 */
function renderSubscriptions(subscriptions) {
    const contentEl = document.getElementById('subscriptions-content');

    if (!subscriptions || subscriptions.length === 0) {
        contentEl.innerHTML = '<p class="loading-subscriptions">No hay suscripciones disponibles</p>';
        return;
    }

    const html = subscriptions.map(sub => {
        const eventInfo = EVENT_LABELS[sub.event_type] || {
            label: sub.event_type,
            icon: '📋',
            description: ''
        };

        return `
            <div class="subscription-item" data-event="${sub.event_type}">
                <div class="subscription-event-title">
                    <span>${eventInfo.icon}</span>
                    <span>${eventInfo.label}</span>
                </div>
                <div class="subscription-channels">
                    ${renderChannelCheckbox(sub, 'email', sub.email_enabled)}
                    ${renderChannelCheckbox(sub, 'sms', sub.sms_enabled)}
                    ${renderChannelCheckbox(sub, 'whatsapp', sub.whatsapp_enabled)}
                </div>
            </div>
        `;
    }).join('');

    contentEl.innerHTML = html;
}

/**
 * Renderiza un checkbox de canal
 */
function renderChannelCheckbox(subscription, channel, enabled) {
    const checkboxId = `sub-${subscription.event_type}-${channel}`;
    return `
        <div class="channel-checkbox">
            <input
                type="checkbox"
                id="${checkboxId}"
                data-event="${subscription.event_type}"
                data-channel="${channel}"
                ${enabled ? 'checked' : ''}
            >
            <label for="${checkboxId}">${CHANNEL_LABELS[channel]}</label>
        </div>
    `;
}

/**
 * Configura los event listeners para los checkboxes
 */
function setupSubscriptionListeners() {
    const contentEl = document.getElementById('subscriptions-content');
    const saveBtn = document.getElementById('btn-save-subscriptions');

    // Delegación de eventos para los checkboxes
    contentEl.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox') {
            hasChanges = true;
            saveBtn.style.display = 'inline-block';
        }
    });

    // Listener para el botón de guardar
    saveBtn.addEventListener('click', saveSubscriptions);
}

/**
 * Guarda las suscripciones actualizadas
 */
async function saveSubscriptions() {
    const saveBtn = document.getElementById('btn-save-subscriptions');
    const originalText = saveBtn.innerHTML;

    try {
        // Mostrar estado de guardando
        saveBtn.disabled = true;
        saveBtn.innerHTML = '⏳ Guardando...';

        // Recopilar los datos de los checkboxes
        const updatedSubscriptions = [];
        const checkboxes = document.querySelectorAll('.channel-checkbox input[type="checkbox"]');

        // Agrupar por evento
        const subscriptionsByEvent = {};

        checkboxes.forEach(checkbox => {
            const eventType = checkbox.dataset.event;
            const channel = checkbox.dataset.channel;
            const enabled = checkbox.checked;

            if (!subscriptionsByEvent[eventType]) {
                subscriptionsByEvent[eventType] = {
                    event_type: eventType,
                    email_enabled: false,
                    sms_enabled: false,
                    whatsapp_enabled: false
                };
            }

            subscriptionsByEvent[eventType][`${channel}_enabled`] = enabled;
        });

        // Convertir a array
        Object.values(subscriptionsByEvent).forEach(sub => {
            updatedSubscriptions.push(sub);
        });

        // Enviar al servidor
        const response = await SubscriptionsAPI.updateSubscriptionsBulk(SUBSCRIPTION_USER_ID, updatedSubscriptions);

        // Actualizar estado local
        currentSubscriptions = response.subscriptions;
        hasChanges = false;

        // Mostrar éxito
        saveBtn.style.display = 'none';
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;

        showToast('✅ Preferencias guardadas exitosamente', 'success');
    } catch (error) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;
        showToast('❌ Error al guardar las preferencias', 'error');
        console.error('Error guardando suscripciones:', error);
    }
}

/**
 * Configurar el botón de colapsar/expandir
 */
function setupCollapseButton() {
    const collapseBtn = document.getElementById('btn-collapse-subscriptions');
    const subscriptionsHeader = document.getElementById('subscriptions-header');
    const subscriptionsPanel = collapseBtn?.closest('.subscriptions-panel');

    if (collapseBtn && subscriptionsPanel) {
        // Handler para el click en el botón
        const toggleCollapse = (e) => {
            e.stopPropagation(); // Evitar que se propague al header
            subscriptionsPanel.classList.toggle('collapsed');

            // Guardar estado en localStorage
            const isCollapsed = subscriptionsPanel.classList.contains('collapsed');
            localStorage.setItem('subscriptions-collapsed', isCollapsed);
        };

        collapseBtn.addEventListener('click', toggleCollapse);

        // También permitir colapsar haciendo click en todo el header
        subscriptionsHeader.addEventListener('click', () => {
            subscriptionsPanel.classList.toggle('collapsed');

            // Guardar estado en localStorage
            const isCollapsed = subscriptionsPanel.classList.contains('collapsed');
            localStorage.setItem('subscriptions-collapsed', isCollapsed);
        });

        // Restaurar estado desde localStorage
        const savedState = localStorage.getItem('subscriptions-collapsed');
        if (savedState === 'true') {
            subscriptionsPanel.classList.add('collapsed');
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    setupCollapseButton();
    initSubscriptionsManager();
});
