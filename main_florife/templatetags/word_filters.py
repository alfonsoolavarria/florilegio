import re
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def format_definition(text):
    if not text:
        return ''
    esc = escape(text)

    # Color references: { Book Chap:Verse} -> dark ocean blue
    with_refs = re.sub(
        r'\{?\s*[\d]*[A-Z]\w+[\s_]\d+:\d+[a-z]?',
        lambda m: f'<span class="ref-highlight">{m.group(0)}</span>',
        esc,
    )

    # Bold cross-references after Véase/Véanse
    def bold_xref(match):
        prefix = match.group(1)
        rest = match.group(2)
        bolded = re.sub(
            r'[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9º()]+',
            r'<strong>\g<0></strong>',
            rest,
        )
        return match.group(0).replace(rest, bolded)

    with_bold_xref = re.sub(
        r'([Vv][eé]anse?|VÉASE|VÉANSE)\s+([^.]*\.)',
        bold_xref,
        with_refs,
    )

    # Mark "Nota:" / "Notas:" with a special class
    with_notes = re.sub(
        r'(?<!\w)(Nota[s]?:)',
        r'<span class="note-label">\1</span>',
        with_bold_xref,
    )

    # Split on major sections: letter + ". "
    parts = re.split(r'(?:^|\b)([A-Z])\.\s+', with_notes)
    formatted = []
    i = 0
    while i < len(parts):
        p = parts[i]
        if not p:
            i += 1
            continue
        if len(p) == 1 and i + 1 < len(parts):
            marker = p
            i += 1
            content = parts[i]
            content = re.sub(
                r'^(\w+)',
                r'<span class="section-label">\1</span>',
                content,
            )
            body = re.sub(
                r'(\d+)\.\s+',
                r'<br><span class="num-item">\1.</span> ',
                content,
            )
            body = re.sub(
                r'\b([a-z]\))\s+',
                r'<br><span class="letter-item">\1</span> ',
                body,
            )
            formatted.append(
                f'<div class="section-block">'
                f'<span class="section-marker">{marker}.</span>&nbsp;{body}'
                f'</div>'
            )
        else:
            body = re.sub(
                r'(\d+)\.\s+',
                r'<br><span class="num-item">\1.</span> ',
                p,
            )
            body = re.sub(
                r'\b([a-z]\))\s+',
                r'<br><span class="letter-item">\1</span> ',
                body,
            )
            formatted.append(f'<div class="para-block">{body}</div>')
        i += 1

    return mark_safe(''.join(formatted))
