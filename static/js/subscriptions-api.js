/**
 * API Client para gestión de suscripciones de notificaciones
 */

const SubscriptionsAPI = {
    /**
     * Obtiene las suscripciones de un usuario
     */
    async getUserSubscriptions(userId) {
        try {
            const response = await fetch(`/api/subscriptions/user/${userId}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error obteniendo suscripciones:', error);
            throw error;
        }
    },

    /**
     * Actualiza una suscripción individual
     */
    async updateSubscription(userId, subscriptionData) {
        try {
            const response = await fetch(`/api/subscriptions/user/${userId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(subscriptionData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error actualizando suscripción:', error);
            throw error;
        }
    },

    /**
     * Actualiza múltiples suscripciones en lote
     */
    async updateSubscriptionsBulk(userId, subscriptionsArray) {
        try {
            const response = await fetch(`/api/subscriptions/user/${userId}/bulk`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    subscriptions: subscriptionsArray
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error actualizando suscripciones en lote:', error);
            throw error;
        }
    },

    /**
     * Obtiene los canales habilitados para un usuario y evento
     */
    async getEnabledChannels(userId, eventType) {
        try {
            const response = await fetch(`/api/subscriptions/user/${userId}/event/${eventType}/channels`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error obteniendo canales habilitados:', error);
            throw error;
        }
    }
};
