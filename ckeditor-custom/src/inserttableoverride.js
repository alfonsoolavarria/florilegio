import { Plugin } from '@ckeditor/ckeditor5-core';
import { ButtonView } from '@ckeditor/ckeditor5-ui';

export default class InsertTableOverride extends Plugin {
    static get pluginName() {
        return 'InsertTableOverride';
    }

    static get requires() {
        return ['TableEditing', 'TableUI'];
    }

    init() {
        const editor = this.editor;

        editor.ui.componentFactory.add('insertTable', (locale) => {
            const button = new ButtonView(locale);
            const command = editor.commands.get('insertTable');

            button.label = 'Insertar tabla';
            button.tooltip = true;
            button.icon = tableIcon;

            button.bind('isEnabled').to(command);

            button.on('execute', () => {
                editor.execute('insertTable', { rows: 3, columns: 3 });
                editor.editing.view.focus();
            });

            return button;
        });
    }
}

const tableIcon = `<svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
  <rect x="3" y="3" width="14" height="14" rx="1" fill="none" stroke="currentColor" stroke-width="1.4"/>
  <line x1="3" y1="8.5" x2="17" y2="8.5" stroke="currentColor" stroke-width="1.4"/>
  <line x1="3" y1="13.5" x2="17" y2="13.5" stroke="currentColor" stroke-width="1.4"/>
  <line x1="8.5" y1="3" x2="8.5" y2="17" stroke="currentColor" stroke-width="1.4"/>
  <line x1="13.5" y1="3" x2="13.5" y2="17" stroke="currentColor" stroke-width="1.4"/>
</svg>`;
