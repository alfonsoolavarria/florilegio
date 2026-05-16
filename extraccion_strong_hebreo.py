import json
import re
import PyPDF2


def extraer_strong_hebreo_definitivo(pdf_path, json_output_path):
    print("Iniciando extracción del Diccionario Hebreo y Arameo...")
    reader = PyPDF2.PdfReader(pdf_path)
    total_paginas = len(reader.pages)
    print(f"Total de páginas en PDF: {total_paginas}")

    # Páginas 12 a 484 (índices 11 a 483)
    paginas_rango = range(11, min(484, total_paginas))

    texto_completo = ""
    for num_pagina in paginas_rango:
        try:
            texto_completo += reader.pages[num_pagina].extract_text() + "\n"
        except Exception as e:
            print(f"Error página {num_pagina + 1}: {e}")

    print(f"Texto extraído: {len(texto_completo)} caracteres")

    pattern = re.compile(r'(\d{1,4})\s*\.\s+')
    matches = list(pattern.finditer(texto_completo))
    print(f"Candidatos encontrados: {len(matches)}")

    entries = []
    for idx, match in enumerate(matches):
        pos = match.start()
        if pos != 0 and texto_completo[pos - 1] != '\n':
            continue

        num_strong = match.group(1)
        start = match.end()

        if idx + 1 < len(matches):
            end = matches[idx + 1].start()
        else:
            end = len(texto_completo)

        bloque = texto_completo[start:end].strip()
        if not bloque:
            continue

        bloque_limpio = bloque.replace('\n', ' ').strip()
        bloque_limpio = re.sub(r'\s+', ' ', bloque_limpio)

        if ':—' in bloque_limpio:
            definicion_parte, traduccion_parte = bloque_limpio.split(':—', 1)
        elif '—' in bloque_limpio:
            definicion_parte, traduccion_parte = bloque_limpio.split('—', 1)
        else:
            definicion_parte = bloque_limpio
            traduccion_parte = ""

        if ';' in definicion_parte:
            transliteracion, resto_definicion = definicion_parte.split(';', 1)
        else:
            transliteracion = definicion_parte
            resto_definicion = ""

        entries.append({
            "strong": num_strong.strip(),
            "transliteracion": transliteracion.strip(),
            "definicion": resto_definicion.strip(),
            "traduccion_rv60": traduccion_parte.strip()
        })

    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump({"diccionario_strong_hebreo": entries}, f, ensure_ascii=False, indent=4)

    print(f"¡Proceso completado!")
    print(f"Entradas extraídas: {len(entries)}")
    print(f"Archivo guardado en: {json_output_path}")

    print("\nPrimeras 3 entradas:")
    for e in entries[:3]:
        print(f"  {e['strong']}. {e['transliteracion'][:60]}...")
    print(f"\nÚltimas 3 entradas:")
    for e in entries[-3:]:
        print(f"  {e['strong']}. {e['transliteracion'][:60]}...")


extraer_strong_hebreo_definitivo('nueva-concordancia-strong.pdf', 'strong_hebreo.json')
