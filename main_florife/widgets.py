from django import forms
from django.utils.safestring import mark_safe


class CKEditorWidget(forms.Textarea):
    class Media:
        js = ('js/ckeditor.js',)
        css = {'all': ('css/ckeditor-admin.css',)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.setdefault('class', 'vLargeTextField ckeditor-ready')

    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        editor_id = attrs.get('id', f'id_{name}')
        return mark_safe(
            html
            + f"""
<script>
document.addEventListener("DOMContentLoaded", () => {{
    const editorEl = document.getElementById("{editor_id}");
    if (!editorEl) return;
    FlorilegioEditor.create(editorEl, {{
        toolbar: {{
            items: [
                "undo", "redo",
                "heading", "|",
                "fontSize", "fontColor", "fontFamily", "|",
                "bold", "italic", "underline", "strikethrough", "code", "|",
                "highlight", "|",
                "alignment", "|",
                "bulletedList", "numberedList", "outdent", "indent", "|",
                "link", "blockQuote", "codeBlock", "insertTable", "|",
                "mediaEmbed", "horizontalLine", "|",
                "emoji", "specialCharacters", "|",
                "findAndReplace", "sourceEditing"
            ],
            shouldNotGroupWhenFull: false
        }},
        language: "es"
    }}).catch(error => console.error("CKEditor error:", error));
}});
</script>
"""
        )
