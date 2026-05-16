import json
import re
import PyPDF2

def extraer_louw_nida_definitivo(pdf_path, json_output_path):
    print("Iniciando la extracción selectiva de Louw-Nida...")
    
    # Diccionario de mapeo para la fuente clásica "Greek-Legacy" a Unicode estándar
    greek_map = {
        'a': 'α', 'b': 'β', 'g': 'γ', 'd': 'δ', 'e': 'ε', 'z': 'ζ', 'h': 'η', 'j': 'θ',
        'i': 'ι', 'k': 'κ', 'l': 'λ', 'm': 'μ', 'n': 'ν', 'x': 'ξ', 'o': 'ο', 'p': 'π',
        'r': 'ρ', 's': 'σ', 'v': 'ς', 't': 'τ', 'u': 'υ', 'f': 'φ', 'c': 'χ', 'y': 'ψ',
        'w': 'ω', 'A': 'Α', 'B': 'Β', 'G': 'Γ', 'D': 'Δ', 'E': 'Ε', 'Z': 'Ζ', 'H': 'Η',
        'J': 'Θ', 'I': 'Ι', 'K': 'Κ', 'L': 'Λ', 'M': 'μ', 'N': 'Ν', 'X': 'Ξ', 'O': 'Ο',
        'P': 'Π', 'R': 'Ρ', 'S': 'Σ', 'T': 'Τ', 'U': 'Υ', 'F': 'Φ', 'C': 'Χ', 'Y': 'Ψ',
        'W': 'Ω',
        '\'': '́', '`': '̀', '~': '͂', '"': '̈', '>': '̓', '<': '̔', '|': 'ͅ',
    }

    def transliterar_palabra_griega(word):
        """Convierte una palabra codificada en fuente antigua a Unicode real."""
        res = ""
        for char in word:
            res += greek_map.get(char, char)
        return res

    def corregir_texto_selectivo(text):
        """Escanea un bloque de texto y traduce a griego solo las palabras bajo la fuente legacy."""
        if not text:
            return ""
        words = text.split(' ')
        words_procesadas = []
        for word in words:
            # Detecta si la palabra tiene marcadores tipográficos exclusivos del griego en este PDF
            if any(c in "vjhw`>~<|" for c in word):
                words_procesadas.append(transliterar_palabra_griega(word))
            else:
                words_procesadas.append(word)
        return ' '.join(words_procesadas)

    reader = PyPDF2.PdfReader(pdf_path)
    entries = []
    
    # Rango de páginas del dominio 1 (pág 25) al dominio 93 (pág 1050).
    # En PyPDF2 los índices son base 0, por lo que la página 25 es el índice 24.
    paginas_rango = range(24, 1050)
    
    # Expresión regular para capturar la estructura:
    # 1. Código de dominio decimal (ej. 1.1 o 93.595) al inicio de bloque/línea
    # 2. Todo el contenido continuo hasta topar con el inicio del siguiente código de dominio
    pattern = re.compile(r'(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+|\Z)', re.DOTALL)
    
    for num_pagina in paginas_rango:
        try:
            texto_pagina = reader.pages[num_pagina].extract_text()
            matches = pattern.findall(texto_pagina)
            
            for code, bloque_completo in matches:
                # Limpiar saltos de línea y normalizar espacios del bloque extraído
                bloque_limpio = bloque_completo.replace('\n', ' ').strip()
                
                # En Louw-Nida, el término principal en griego se separa del cuerpo por dos puntos ':'
                if ':' in bloque_limpio:
                    termino_raw, cuerpo_raw = bloque_limpio.split(':', 1)
                else:
                    termino_raw = bloque_limpio
                    cuerpo_raw = ""
                
                # El término principal SIEMPRE es griego, se translitera por completo
                termino_griego = transliterar_palabra_griega(termino_raw.strip())
                
                # El cuerpo contiene una mezcla de inglés (definiciones) y griego (ejemplos).
                # Lo procesamos con el filtro selectivo por partes para proteger las glosas ‘...’
                partes = re.split(r'(‘|’)', cuerpo_raw)
                partes_corregidas = []
                
                for parte in partes:
                    if parte in ['‘', '’']:
                        partes_corregidas.append(parte)
                    elif any(c in "vjhw`>~<|" for c in parte):
                        # Si la sección del texto contiene rastros de la fuente griega, la procesamos palabra por palabra
                        partes_corregidas.append(corregir_texto_selectivo(parte))
                    else:
                        # Si es inglés puro de la definición, se mantiene intacto
                        partes_corregidas.append(parte)
                        
                definicion_completa = "".join(partes_corregidas).strip()
                
                # Extraemos la glosa principal (la primera traducción corta entre comillas simples)
                glosa_match = re.search(r'‘(.*?)’', definicion_completa)
                glosa_principal = glosa_match.group(1) if glosa_match else ""
                
                entries.append({
                    "id": code.strip(),
                    "termino_griego": termino_griego,
                    "definicion_completa": definicion_completa,
                    "glosa_principal": glosa_principal
                })
        except Exception as e:
            print(f"Error en página {num_pagina + 1}: {str(e)}")
            continue

    # Guardar en JSON con codificación UTF-8 para almacenar nativamente los caracteres Unicode
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump({"louw_nida_completo": entries}, f, ensure_ascii=False, indent=4)
        
    print(f"¡Proceso completado con éxito! Se extrajeron {len(entries)} dominios semánticos.")
    print(f"Archivo JSON guardado en: {json_output_path}")

# Ejecución del script en el entorno local
pdf_nombre = 'Greek-English Lexicon of the New Testament Based on Semantic Domains by J. P. Louw and Eugene Albert Nida Volume I] 1989.pdf'
extraer_louw_nida_definitivo(pdf_nombre, 'louw_nida_final.json')