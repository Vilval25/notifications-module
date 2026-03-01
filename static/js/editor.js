/**
 * Editor WYSIWYG con Quill.js para plantillas Handlebars
 */
class TemplateEditor {
    constructor(elementId) {
        // Configurar Quill con toolbar personalizado
        this.quill = new Quill(`#${elementId}`, {
            theme: 'snow',
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, false] }],
                    ['bold', 'italic', 'underline'],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                    [{ 'align': [] }],
                    [{ 'color': [] }, { 'background': [] }],
                    ['link'],
                    ['clean']
                ]
            },
            placeholder: 'Escribe tu plantilla aquí...'
        });

        this.changeListeners = [];

        // Event listener para cambios
        this.quill.on('text-change', () => {
            this.notifyChange();
        });
    }

    /**
     * Obtener HTML del editor
     * Nota: Quill genera HTML, las variables Handlebars se mantienen intactas
     */
    getValue() {
        const html = this.quill.root.innerHTML;

        // Si está vacío, retornar string vacío
        if (html === '<p><br></p>') {
            return '';
        }

        return html;
    }

    /**
     * Establecer contenido HTML en el editor
     */
    setValue(htmlContent) {
        if (!htmlContent || htmlContent.trim() === '') {
            this.quill.setText('');
        } else {
            // Usar clipboard para mejor manejo de HTML complejo
            const delta = this.quill.clipboard.convert(htmlContent);
            this.quill.setContents(delta, 'silent');
        }
    }

    /**
     * Insertar variable Handlebars en la posición del cursor
     */
    insertVariable(variable) {
        const range = this.quill.getSelection(true);

        if (range) {
            // Insertar la variable como texto sin formato especial
            this.quill.insertText(range.index, variable, 'user');

            // Mover cursor al final de la variable insertada
            this.quill.setSelection(range.index + variable.length);

            // Dar foco al editor
            this.quill.focus();
        } else {
            // Si no hay selección, insertar al final
            const length = this.quill.getLength();
            this.quill.insertText(length - 1, variable, 'user');
            this.quill.setSelection(length + variable.length - 1);
        }
    }

    /**
     * Limpiar contenido del editor
     */
    clear() {
        this.quill.setText('');
    }

    /**
     * Habilitar/deshabilitar editor
     */
    setReadOnly(readOnly) {
        this.quill.enable(!readOnly);
    }

    /**
     * Registrar callback para cambios
     */
    onChange(callback) {
        this.changeListeners.push(callback);
    }

    /**
     * Notificar a todos los listeners de cambios
     */
    notifyChange() {
        const content = this.getValue();
        this.changeListeners.forEach(cb => cb(content));
    }

    /**
     * Dar foco al editor
     */
    focus() {
        this.quill.focus();
    }

    /**
     * Obtener texto plano (sin HTML)
     */
    getText() {
        return this.quill.getText();
    }

    /**
     * Verificar si el editor está vacío
     */
    isEmpty() {
        return this.quill.getText().trim().length === 0;
    }
}
