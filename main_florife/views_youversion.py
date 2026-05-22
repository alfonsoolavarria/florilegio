import requests
import re
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_GET
import os

YVP_API_URL = "https://api.youversion.com/v1"
YVP_APP_KEY = os.environ.get("YVP_APP_KEY", getattr(settings, 'YVP_APP_KEY', 'vPQyIxSLnLbnPgg8Avm1T24kVIgyoaUpyLAUw6dll2BFqoXJ'))

USFM_MAPPING = {
    1: 'GEN', 2: 'EXO', 3: 'LEV', 4: 'NUM', 5: 'DEU', 6: 'JOS', 7: 'JDG', 8: 'RUT',
    9: '1SA', 10: '2SA', 11: '1KI', 12: '2KI', 13: '1CH', 14: '2CH', 15: 'EZR', 16: 'NEH',
    17: 'EST', 18: 'JOB', 19: 'PSA', 20: 'PRO', 21: 'ECC', 22: 'SNG', 23: 'ISA', 24: 'JER',
    25: 'LAM', 26: 'EZK', 27: 'DAN', 28: 'HOS', 29: 'JOL', 30: 'AMO', 31: 'OBA', 32: 'JON',
    33: 'MIC', 34: 'NAM', 35: 'HAB', 36: 'ZEP', 37: 'HAG', 38: 'ZEC', 39: 'MAL',
    40: 'MAT', 41: 'MRK', 42: 'LUK', 43: 'JHN', 44: 'ACT', 45: 'ROM', 46: '1CO', 47: '2CO',
    48: 'GAL', 49: 'EPH', 50: 'PHP', 51: 'COL', 52: '1TH', 53: '2TH', 54: '1TI', 55: '2TI',
    56: 'TIT', 57: 'PHM', 58: 'HEB', 59: 'JAS', 60: '1PE', 61: '2PE', 62: '1JN', 63: '2JN',
    64: '3JN', 65: 'JUD', 66: 'REV'
}

YOUVERSION_BIBLES = [
    {'id': 103, 'name': 'Nueva Biblia de las Américas', 'abbreviation': 'NBLA'},
    {'id': 147, 'name': 'Reina-Valera Antigua', 'abbreviation': 'RVA'},
    {'id': 128, 'name': 'Nueva Versión Internacional 2025', 'abbreviation': 'NVI-S'},
    {'id': 89, 'name': 'La Biblia de las Américas', 'abbreviation': 'LBLA'},
    {'id': 2664, 'name': 'Nueva Versión Internacional 2015', 'abbreviation': 'NVI-S'},
    {'id': 3291, 'name': 'Versión Biblia Libre', 'abbreviation': 'VBL'},
    {'id': 3365, 'name': 'Palabra de Dios para ti', 'abbreviation': 'PdDpt'},
    {'id': 4212, 'name': 'Gloss Spanish', 'abbreviation': 'GlossSP'},
]


@require_GET
def youversion_bibles(request):
    return JsonResponse({'data': YOUVERSION_BIBLES})


@require_GET
def youversion_chapter(request):
    bible_id = request.GET.get('bible_id')
    book_num = request.GET.get('book')
    chapter = request.GET.get('chapter')

    if not all([bible_id, book_num, chapter]):
        return JsonResponse({
            'status': 'error',
            'message': 'Faltan parámetros requeridos (bible_id, book, chapter).'
        }, status=400)

    try:
        book_num = int(book_num)
    except (ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'book debe ser un número.'}, status=400)

    usfm_book = USFM_MAPPING.get(book_num)
    if not usfm_book:
        return JsonResponse({'status': 'error', 'message': f'Libro no válido: {book_num}'}, status=400)

    passage_id = f"{usfm_book}.{chapter}"
    url = f"{YVP_API_URL}/bibles/{bible_id}/passages/{passage_id}?format=html"

    try:
        response = requests.get(url, headers={'X-YVP-App-Key': YVP_APP_KEY}, timeout=15)
    except requests.RequestException:
        return JsonResponse({
            'status': 'error',
            'message': 'Hubo un problema con la información de la Biblia. Por favor, intenta más tarde.',
            'youversion_error': True
        }, status=503)

    if response.status_code != 200:
        return JsonResponse({
            'status': 'error',
            'message': 'Hubo un problema con la información de la Biblia. Por favor, intenta más tarde.',
            'youversion_error': True
        }, status=503)

    try:
        data = response.json()
    except ValueError:
        return JsonResponse({
            'status': 'error',
            'message': 'Hubo un problema con la información de la Biblia. Por favor, intenta más tarde.',
            'youversion_error': True
        }, status=503)

    content_html = data.get('data', data)
    if isinstance(content_html, dict):
        content_html = content_html.get('content', '')

    verses = _parse_youversion_html(content_html)

    if not verses:
        return JsonResponse({
            'status': 'error',
            'message': 'No se encontraron versículos en esta selección.',
        }, status=404)

    clean_html = _clean_youversion_html(content_html)

    return JsonResponse({
        'status': 'success',
        'data': verses,
        'html': clean_html,
        'source': 'youversion',
        'reference': data.get('reference', '') if isinstance(data, dict) else ''
    })


def _parse_youversion_html(html):
    verses = []
    pattern = r'<span\s+class="yv-v"\s+v="(\d+)"[^>]*></span><span\s+class="yv-vlbl"[^>]*>\d+</span>(.*?)(?=<span\s+class="yv-v"\s+v="(\d+)"|\s*</div>\s*</div>\s*$)'

    parts = re.split(r'<span\s+class="yv-v"\s+v="(\d+)"[^>]*></span><span\s+class="yv-vlbl"[^>]*>\d+</span>', html)

    if len(parts) < 2:
        return verses

    first_verse_num = int(parts[1])
    text_parts = parts[2:]

    for i in range(0, len(text_parts), 2):
        verse_num = first_verse_num + (i // 2)
        text = text_parts[i] if i < len(text_parts) else ''

        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('¶', '').strip()
        text = re.sub(r'\s+', ' ', text)

        if text:
            verses.append({'versiculo': verse_num, 'texto': text})

    if parts[1]:
        first_text = re.sub(r'<[^>]+>', '', parts[2] if len(parts) > 2 else '')
        first_text = first_text.replace('¶', '').strip()
        first_text = re.sub(r'\s+', ' ', first_text)
        if first_text:
            verses.insert(0, {'versiculo': int(parts[1]), 'texto': first_text})

    unique = {}
    for v in verses:
        if v['versiculo'] not in unique:
            unique[v['versiculo']] = v
    return list(unique.values())


def _clean_youversion_html(html):
    html = html.strip()
    html = re.sub(r'^\s*<div>\s*', '', html)
    html = re.sub(r'\s*</div>\s*$', '', html)
    html = re.sub(r'<span class="yv-v" v="\d+"></span>', '', html)
    html = re.sub(
        r'<span class="yv-vlbl">(\d+)</span>',
        r'<sup class="yv-verse-num text-primary fw-bold me-1" style="font-size:0.72rem;">\1</sup>',
        html
    )
    html = html.replace('<div class="p">', '<div class="p" style="margin-bottom: 1.25rem;">')
    return html
