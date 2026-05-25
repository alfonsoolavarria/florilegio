import requests
import json
import os
import re
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta
from bs4 import BeautifulSoup
from .models import ApiBibleSyncStatus, VersiculoBiblia

API_BIBLE_URL = "https://rest.api.bible/v1/bibles"
API_KEY = os.environ.get("BIBLE_API_KEY") or getattr(settings, 'BIBLE_API_KEY', None)

VERSIONS_INFO = {
    'nbla': {'id': 'ce11b813f9a27e20-01', 'name': 'Nueva Biblia de las Américas'},
    'ntv': {'id': '826f63861180e056-01', 'name': 'Nueva Traducción Viviente'},
    'rvr09': {'id': '592420522e16049f-01', 'name': 'Reina Valera 1909'},
}

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

def get_headers():
    return {
        'api-key': API_KEY,
        'accept': 'application/json'
    }

@staff_member_required
def api_bible_status(request):
    """Devuelve el estado de las 3 biblias para el panel de Control."""
    statuses = []
    now = timezone.now()
    
    for version_key, info in VERSIONS_INFO.items():
        obj, created = ApiBibleSyncStatus.objects.get_or_create(version=version_key)
        days_passed = 30
        if obj.last_synced_at:
            delta = now - obj.last_synced_at
            days_passed = delta.days
            
        needs_sync = days_passed >= 30 or created
        
        # Check if we have verses for this version
        verses_count = VersiculoBiblia.objects.filter(version=version_key).count()
        if verses_count == 0:
            needs_sync = True
            
        statuses.append({
            'key': version_key,
            'name': info['name'],
            'days_passed': days_passed,
            'needs_sync': needs_sync,
            'sync_date': obj.last_synced_at.strftime('%Y-%m-%d %H:%M') if obj.last_synced_at and not created else 'Nunca'
        })
    return JsonResponse({'statuses': statuses})

@staff_member_required
def api_bible_sync_book_setup(request, version_key):
    """Devuelve la lista de libros a sincronizar (1 al 66)."""
    return JsonResponse({'books': list(USFM_MAPPING.keys())})

@staff_member_required
def api_bible_sync_chapter(request, version_key, libro_num, capitulo_num):
    """Extrae UN capítulo de API Bible, lo parsea, y lo guarda en DB."""
    if version_key not in VERSIONS_INFO:
        return JsonResponse({'error': 'Versión no válida'}, status=400)
        
    bible_id = VERSIONS_INFO[version_key]['id']
    usfm_book = USFM_MAPPING.get(libro_num)
    if not usfm_book:
        return JsonResponse({'error': 'Libro no válido'}, status=400)
    
    chapter_id = f"{usfm_book}.{capitulo_num}"
    url = f"{API_BIBLE_URL}/{bible_id}/chapters/{chapter_id}?content-type=html&include-notes=false&include-titles=false&include-chapter-numbers=false&include-verse-numbers=true&include-verse-spans=false"
    
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200:
        if response.status_code == 404:
             return JsonResponse({'error': 'Not found', 'end_of_book': True})
        return JsonResponse({'error': f"Error de la API: {response.status_code}"}, status=400)
        
    data = response.json().get('data', {})
    content = data.get('content', '')
    
    soup = BeautifulSoup(content, 'html.parser')
    
    for tag in soup.find_all(['p', 'q', 'm', 'b', 'pb']):
        tag.insert(0, '¶')
        
    verse_html_chunks = {}
    current_verse = 0
    buffer_str = ""
    
    for element in soup.descendants:
        if isinstance(element, str):
            # Skip the visual verse number itself
            if element.parent and element.parent.name == 'span' and 'v' in element.parent.get('class', []):
                continue
                
            if current_verse > 0:
                verse_html_chunks[current_verse] += buffer_str + element
                buffer_str = ""
            else:
                buffer_str += element
        elif hasattr(element, 'name') and element.name == 'span' and 'v' in element.get('class', []):
            verse_str = element.get('data-number')
            try:
                current_verse = int(verse_str.split('-')[0])
                if current_verse not in verse_html_chunks:
                    verse_html_chunks[current_verse] = ""
            except:
                pass

    if not verse_html_chunks:
         return JsonResponse({'error': 'No verses found', 'end_of_book': True})

    # Prepare for Bulk Create or Replace
    VersiculoBiblia.objects.filter(version=version_key, libro=libro_num, capitulo=capitulo_num).delete()
    
    objects_to_create = []
    for v_num, text in verse_html_chunks.items():
        clean_text = text.replace('\n', ' ')
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        objects_to_create.append(VersiculoBiblia(
            version=version_key,
            libro=libro_num,
            capitulo=capitulo_num,
            versiculo=v_num,
            texto=clean_text
        ))
    
    VersiculoBiblia.objects.bulk_create(objects_to_create)
    return JsonResponse({'success': True, 'verses_imported': len(objects_to_create)})

@staff_member_required
def api_bible_finish_sync(request, version_key):
    """Actualiza la fecha de sincronización tras terminar todos los libros."""
    obj, _ = ApiBibleSyncStatus.objects.get_or_create(version=version_key)
    obj.last_synced_at = timezone.now()
    obj.save()
    return JsonResponse({'success': True})
