import json, re, urllib.request, urllib.error, time, sys

BASE = "https://www.bibliaya.com"

SLEEP = 0.3

OT_SLUGS = [
    "genesis","exodo","levitico","numeros","deuteronomio",
    "josue","jueces","rut","1samuel","2samuel","1reyes","2reyes",
    "1cronicas","2cronicas","esdras","nehemias","ester","job",
    "salmos","proverbios","eclesiastes","cantares",
    "isaias","jeremias","lamentaciones","ezequiel","daniel",
    "oseas","joel","amos","abdias","jonas","miqueas",
    "nahum","habacuc","sofonias","hageo","zacarias","malaquias",
]

BOOK_NAMES = {
    "genesis":"Génesis","exodo":"Éxodo","levitico":"Levítico",
    "numeros":"Números","deuteronomio":"Deuteronomio",
    "josue":"Josué","jueces":"Jueces","rut":"Rut",
    "1samuel":"1 Samuel","2samuel":"2 Samuel",
    "1reyes":"1 Reyes","2reyes":"2 Reyes",
    "1cronicas":"1 Crónicas","2cronicas":"2 Crónicas",
    "esdras":"Esdras","nehemias":"Nehemías","ester":"Ester",
    "job":"Job","salmos":"Salmos","proverbios":"Proverbios",
    "eclesiastes":"Eclesiastés","cantares":"Cantares",
    "isaias":"Isaías","jeremias":"Jeremías",
    "lamentaciones":"Lamentaciones","ezequiel":"Ezequiel",
    "daniel":"Daniel","oseas":"Oseas","joel":"Joel",
    "amos":"Amós","abdias":"Abdías","jonas":"Jonás",
    "miqueas":"Miqueas","nahum":"Nahúm","habacuc":"Habacuc",
    "sofonias":"Sofonías","hageo":"Hageo","zacarias":"Zacarías",
    "malaquias":"Malaquías",
}

# Gramcord / TEI morphological codes (not Spanish words)
MORPH_CODES = frozenset([
    "Pu", "H", "CK", "PM", "Pt", "XN", "Am", "PL", "h", "NC", "Pb", "Po",
    "Pr", "Pd", "Pi", "Pp", "Nr", "Nb", "Nc", "Vq", "Vp", "Vi", "Vr",
    "Va", "Vm", "Vd", "Vn", "Vx", "R", "T", "C",
])

def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; RVS-Scraper/1.0)"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            print(f"  ERROR: {e}", file=sys.stderr)
            return None

def get_chapters(slug):
    html = fetch(f"{BASE}/libro-{slug}-rvs")
    if not html:
        return []
    chs = re.findall(rf"/version-rvs-{re.escape(slug)}-(\d+)", html)
    return sorted(set(chs), key=int)

def parse_words_from_verse(verse_html):
    """
    Extract (word, strong_number) pairs from the verse HTML fragment.
    
    HTML structure:
      <a class="datos_versiculos cont">
        Y la tierra <a href='...H776-chg'>H776 </a>
        estaba <a href='...H1961-chg'>H1961 </a>
        ...
      </a>
    
    Each Strong's <a> tag is placed right after the Spanish word it annotates.
    Some tags have morphological codes between </a> and the next <a>.
    """
    words = []
    prev_end = 0
    for m in re.finditer(
        r'<a\s+href=[\'"][^\'"]*buscar-([HG]\d+)-chg[\'"]\s*>\s*[HG]\d+\s*</a>',
        verse_html, re.IGNORECASE
    ):
        pre = verse_html[prev_end:m.start()]
        strong = m.group(1)
        prev_end = m.end()

        pre = re.sub(r'<[^>]+>', ' ', pre)
        tokens = pre.split()

        if not tokens:
            continue

        candidates = []
        for tok in reversed(tokens):
            clean = tok.strip(" ,.;:!?-\u00a0")
            if not clean or clean == "\u2022":
                continue
            if clean in MORPH_CODES or (clean.isupper() and len(clean) <= 3):
                continue
            candidates.append(clean)
            break

        if candidates:
            words.append({"word": candidates[0], "strong": strong})

    return words

def parse_chapter(html):
    verses = []
    rows = re.split(r'<tr[^>]*class=[\'"]fila_datos\s*[\'"]?[^>]*>', html)
    for row in rows[1:]:
        ref_m = re.search(
            r'<td[^>]*class=[\'"]t1[\'"]?[^>]*>.*?<a[^>]*>([^<]+)</a>',
            row
        )
        if not ref_m:
            continue
        ref = ref_m.group(1).strip()

        t2_m = re.search(
            r'<td[^>]*class=[\'"]t2[\'"]?[^>]*>(.*?)</tr>', row, re.DOTALL
        )
        if not t2_m:
            continue
        t2 = t2_m.group(1)

        words = parse_words_from_verse(t2)

        rm = re.match(r'(\w+)\s*(\d+):(\d+)', ref)
        ch = int(rm.group(2)) if rm else 0
        vs = int(rm.group(3)) if rm else 0

        verses.append({
            "reference": ref,
            "chapter": ch,
            "verse": vs,
            "words": words,
        })

    return verses

def scrape_all(output_file="rvs_strongs_ot.json"):
    all_data = {}
    for slug in OT_SLUGS:
        name = BOOK_NAMES.get(slug, slug)
        print(f"Scraping {name} ({slug})...", flush=True)
        chapters = get_chapters(slug)
        if not chapters:
            print(f"  No chapters found")
            continue
        book_data = {"name": name, "slug": slug, "chapters": {}}
        for ch in chapters:
            html = fetch(f"{BASE}/version-rvs-{slug}-{ch}")
            if not html:
                print(f"  Ch {ch} FAILED", flush=True)
                continue
            verses = parse_chapter(html)
            book_data["chapters"][int(ch)] = verses
            print(f"  Ch {ch}: {len(verses)}v", flush=True)
            time.sleep(SLEEP)
        all_data[slug] = book_data
        print(f"  Done: {name}", flush=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=1)
    print(f"\nSaved to {output_file}", flush=True)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "rvs_strongs_ot.json"
    scrape_all(out)
