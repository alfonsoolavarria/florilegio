import { ClassicEditor as ClassicEditorBase } from 'ckeditor5';
import 'ckeditor5/dist/ckeditor5.css';
import 'ckeditor5/dist/ckeditor5-editor.css';
import 'ckeditor5/dist/ckeditor5-content.css';
import { Essentials } from '@ckeditor/ckeditor5-essentials';
import { Paragraph } from '@ckeditor/ckeditor5-paragraph';
import { Heading } from '@ckeditor/ckeditor5-heading';
import { Bold, Italic, Underline, Strikethrough, Code, Subscript, Superscript } from '@ckeditor/ckeditor5-basic-styles';
import { Font } from '@ckeditor/ckeditor5-font';
import { Highlight } from '@ckeditor/ckeditor5-highlight';
import { RemoveFormat } from '@ckeditor/ckeditor5-remove-format';
import { Alignment } from '@ckeditor/ckeditor5-alignment';
import { Link } from '@ckeditor/ckeditor5-link';
import { List, TodoList } from '@ckeditor/ckeditor5-list';
import { BlockQuote } from '@ckeditor/ckeditor5-block-quote';
import { CodeBlock } from '@ckeditor/ckeditor5-code-block';
import { Indent, IndentBlock } from '@ckeditor/ckeditor5-indent';

import { Table, TableToolbar, TableCellProperties, TableProperties } from '@ckeditor/ckeditor5-table';
import { MediaEmbed } from '@ckeditor/ckeditor5-media-embed';
import { HorizontalLine } from '@ckeditor/ckeditor5-horizontal-line';
import { SelectAll } from '@ckeditor/ckeditor5-select-all';
import { FindAndReplace } from '@ckeditor/ckeditor5-find-and-replace';
import { SourceEditing } from '@ckeditor/ckeditor5-source-editing';
import { Undo } from '@ckeditor/ckeditor5-undo';
import { WordCount } from '@ckeditor/ckeditor5-word-count';
import { SpecialCharacters, SpecialCharactersEssentials } from '@ckeditor/ckeditor5-special-characters';
import { Emoji } from '@ckeditor/ckeditor5-emoji';
import esTranslations from 'ckeditor5/dist/translations/es.js';
import InsertTableOverride from './inserttableoverride';

class FlorilegioEditor extends ClassicEditorBase {}

FlorilegioEditor.builtinPlugins = [
    Essentials,
    Paragraph,
    Heading,
    Bold,
    Italic,
    Underline,
    Strikethrough,
    Code,
    Subscript,
    Superscript,
    Font,
    Highlight,
    RemoveFormat,
    Alignment,
    Link,
    List,
    TodoList,
    BlockQuote,
    CodeBlock,
    Indent,
    IndentBlock,

    Table,
    TableToolbar,
    TableCellProperties,
    TableProperties,
    MediaEmbed,
    HorizontalLine,
    SelectAll,
    FindAndReplace,
    SourceEditing,
    Undo,
    WordCount,
    SpecialCharacters,
    SpecialCharactersEssentials,
    Emoji,
    InsertTableOverride
];

FlorilegioEditor.defaultConfig = {
    licenseKey: 'GPL',
    translations: esTranslations,
    toolbar: {
        items: [
            'undo', 'redo',
            '|',
            'heading',
            '|',
            'fontColor', 'fontBackgroundColor', 'fontSize', 'fontFamily',
            '|',
            'bold', 'italic', 'underline', 'strikethrough', 'code', 'subscript', 'superscript',
            '|',
            'highlight', 'removeFormat',
            '|',
            'alignment',
            '|',
            'bulletedList', 'numberedList', 'todoList',
            '|',
            'outdent', 'indent',
            '|',
            'link', 'blockQuote', 'codeBlock',
            '|',
            'insertTable', 'mediaEmbed', 'horizontalLine',
            '|',
            'emoji', 'specialCharacters',
            '|',
            'findAndReplace', 'sourceEditing', 'selectAll',
            '|',
            'wordCount'
        ]
    },
    alignment: {
        options: ['left', 'center', 'right', 'justify']
    },
    table: {
        contentToolbar: [
            'tableColumn', 'tableRow', 'mergeTableCells',
            'tableCellProperties', 'tableProperties'
        ],
    },
    heading: {
        options: [
            { model: 'paragraph', title: 'Párrafo', class: 'ck-heading_paragraph' },
            { model: 'heading1', view: 'h1', title: 'Título 1', class: 'ck-heading_heading1' },
            { model: 'heading2', view: 'h2', title: 'Título 2', class: 'ck-heading_heading2' },
            { model: 'heading3', view: 'h3', title: 'Título 3', class: 'ck-heading_heading3' }
        ]
    },
    fontSize: {
        options: [9, 11, 13, 16, 19, 22, 28, 36, 48]
    },
    fontFamily: {
        options: [
            'default',
            'Arial, Helvetica, sans-serif',
            'Georgia, serif',
            'Courier New, Courier, monospace',
            'Verdana, Geneva, sans-serif',
            'Times New Roman, Times, serif'
        ]
    },
    highlight: {
        options: [
            { model: 'yellowMarker', class: 'marker-yellow', title: 'Marcador amarillo', color: 'var(--ck-highlight-marker-yellow)', type: 'marker' },
            { model: 'greenMarker', class: 'marker-green', title: 'Marcador verde', color: 'var(--ck-highlight-marker-green)', type: 'marker' },
            { model: 'pinkMarker', class: 'marker-pink', title: 'Marcador rosa', color: 'var(--ck-highlight-marker-pink)', type: 'marker' },
            { model: 'blueMarker', class: 'marker-blue', title: 'Marcador azul', color: 'var(--ck-highlight-marker-blue)', type: 'marker' },
            { model: 'redPen', class: 'pen-red', title: 'Texto rojo', color: 'var(--ck-highlight-pen-red)', type: 'pen' },
            { model: 'greenPen', class: 'pen-green', title: 'Texto verde', color: 'var(--ck-highlight-pen-green)', type: 'pen' }
        ]
    },
    link: {
        addTargetToExternalLinks: true,
        defaultProtocol: 'https://'
    },
    placeholder: 'Escribe tus reflexiones, pega textos o realiza tu bosquejo aquí...'
};

export default FlorilegioEditor;
