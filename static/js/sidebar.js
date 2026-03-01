/**
 * Manejo de la barra lateral colapsable
 */
class Sidebar {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.toggleBtn = document.getElementById('btn-toggle-sidebar');
        this.isExpanded = this.loadState();

        this.init();
    }

    init() {
        // Aplicar estado inicial
        this.applyState();

        // Event listener para el botón toggle
        if (this.toggleBtn) {
            this.toggleBtn.addEventListener('click', () => this.toggle());
        }
    }

    toggle() {
        this.isExpanded = !this.isExpanded;
        this.applyState();
        this.saveState();
    }

    applyState() {
        if (this.sidebar) {
            if (this.isExpanded) {
                this.sidebar.classList.remove('collapsed');
            } else {
                this.sidebar.classList.add('collapsed');
            }
        }
    }

    saveState() {
        try {
            localStorage.setItem('sidebar-expanded', this.isExpanded.toString());
        } catch (e) {
            console.error('Error guardando estado del sidebar:', e);
        }
    }

    loadState() {
        try {
            const saved = localStorage.getItem('sidebar-expanded');
            // Por defecto expandida si no hay valor guardado
            return saved === null ? true : saved === 'true';
        } catch (e) {
            console.error('Error cargando estado del sidebar:', e);
            return true;
        }
    }
}
