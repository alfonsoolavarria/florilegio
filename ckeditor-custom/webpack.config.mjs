import path from 'path';
import { fileURLToPath } from 'url';
import { loaders } from '@ckeditor/ckeditor5-dev-utils';
import { CKEditorTranslationsPlugin } from '@ckeditor/ckeditor5-dev-translations';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default {
    entry: path.resolve(__dirname, 'src', 'ckeditor.js'),
    output: {
        path: path.resolve(__dirname, '..', 'static'),
        filename: 'js/ckeditor.js',
        library: 'FlorilegioEditor',
        libraryTarget: 'umd',
        libraryExport: 'default',
    },
    module: {
        rules: [
            {
                test: /ckeditor5-[^/\\]+[/\\]theme[/\\]icons[/\\][^/\\]+\.svg$/,
                use: ['raw-loader']
            },
            loaders.getStylesLoader({ minify: true, sourceMap: false }),
            loaders.getIconsLoader()
        ]
    },
    plugins: [
        new CKEditorTranslationsPlugin({
            language: 'es',
            additionalLanguages: 'all'
        })
    ],
    resolve: {
        extensions: ['.js', '.json'],
        alias: {
            'ckeditor5': path.resolve(__dirname, 'node_modules', 'ckeditor5'),
            'ckeditor5-premium-features': path.resolve(__dirname, 'node_modules', 'ckeditor5-premium-features')
        }
    },
    performance: {
        hints: false
    }
};
