import json
import re
import PyPDF2


def extraer_strong_griego_definitivo(pdf_path, json_output_path):
    print("Iniciando extracción del Diccionario Griego...")
    reader = PyPDF2.PdfReader(pdf_path)
    total_paginas = len(reader.pages)
    print(f"Total de páginas en PDF: {total_paginas}")

    # Páginas 493 a 719 (índices 492 a 718)
    paginas_rango = range(492, min(719, total_paginas))

    # Concatenar todo el texto de las páginas relevantes
    texto_completo = ""
    for num_pagina in paginas_rango:
        try:
            texto_completo += reader.pages[num_pagina].extract_text() + "\n"
        except Exception as e:
            print(f"Error página {num_pagina + 1}: {e}")

    print(f"Texto extraído: {len(texto_completo)} caracteres")

    # Encontrar TODAS las posiciones de números Strong en el texto
    # Formato: número (1-4 dígitos), opcionalmente con espacio antes del punto
    # Ej: "1. " o "1448. " o "2804 . "
    pattern = re.compile(r'(\d{1,4})\s*\.\s+')

    matches = list(pattern.finditer(texto_completo))
    print(f"Candidatos encontrados: {len(matches)}")

    entries = []
    for idx, match in enumerate(matches):
        # Solo entradas que empiezan al inicio de línea (no referencias cruzadas inline)
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
            termino_griego, resto_definicion = definicion_parte.split(';', 1)
        else:
            termino_griego = definicion_parte
            resto_definicion = ""

        entries.append({
            "strong": num_strong.strip(),
            "termino_griego": termino_griego.strip(),
            "definicion": resto_definicion.strip(),
            "traduccion_rv60": traduccion_parte.strip()
        })

    # Guardar
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump({"diccionario_strong_griego": entries}, f, ensure_ascii=False, indent=4)

    print(f"¡Proceso completado!")
    print(f"Entradas extraídas: {len(entries)}")
    print(f"Archivo guardado en: {json_output_path}")

    # Mostrar algunos ejemplos
    print("\nPrimeras 3 entradas:")
    for e in entries[:3]:
        print(f"  {e['strong']}. {e['termino_griego'][:60]}...")
    print(f"\nÚltimas 3 entradas:")
    for e in entries[-3:]:
        print(f"  {e['strong']}. {e['termino_griego'][:60]}...")


extraer_strong_griego_definitivo('nueva-concordancia-strong.pdf', 'yo_strong_griego_final.json')
