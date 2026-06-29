#!/usr/bin/env python3
"""
GrupLAC CSV → Astro publications importer.

Reads tab/quote-delimited CSV exports from INFO/productos_gruplac/, enriches
entries that have a DOI via Crossref (full author list, abstract, metadata),
falls back to Semantic Scholar for missing abstracts, then writes .md files
to src/content/publications/.

Usage:
  python scripts/import_gruplac.py             # full import
  python scripts/import_gruplac.py --dry-run   # parse only, no files written
  python scripts/import_gruplac.py --no-enrich # skip Crossref / S2 calls
"""
import csv
import re
import sys
import time
import unicodedata
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────

SCRIPT_DIR    = Path(__file__).parent
PROJECT_DIR   = SCRIPT_DIR.parent
CSV_DIR       = PROJECT_DIR / "INFO" / "productos_gruplac"
OUTPUT_DIR    = PROJECT_DIR / "src" / "content" / "publications"
YEAR_MIN      = 2000
YEAR_MAX      = 2026
CONTACT_EMAIL = "jleongomez@unbosque.edu.co"
REQUEST_DELAY = 0.4   # seconds between API calls

DRY_RUN    = "--dry-run"    in sys.argv
NO_ENRICH  = "--no-enrich"  in sys.argv
HEADERS    = {"User-Agent": f"CODEC-import/1.0 (mailto:{CONTACT_EMAIL})"}

# ── CSV file → pub_type ───────────────────────────────────────────────────────

FILE_TYPE: dict[str, str] = {
    "articulos.csv":                     "article",
    "otro_articulos.csv":                "article",
    "Otra_publicación_divulgativa.csv":  "other",
    "libros.csv":                        "book",
    "libros_formacion.csv":              "book",
    "manuales.csv":                      "book",
    "otros_libros.csv":                  "book",
    "capitulos.csv":                     "book-chapter",
    "documentos_de_trabajo.csv":         "preprint",
}

# ── Researcher matching ───────────────────────────────────────────────────────
# slug, last-name tokens, first-name tokens  (all ASCII-lowercase, no accents)

RESEARCHERS = [
    ("juan-david-leongomez",     ["leongomez"],           ["juan"]),
    ("oscar-sanchez",            ["sanchez"],             ["oscar"]),
    ("ana-maria-salazar",        ["salazar"],             ["ana"]),
    ("milena-vasquez-amezquita", ["vasquez", "amezquita"], ["milena"]),
    ("fidel-mauricio-bonilla",   ["bonilla"],             ["fidel", "mauricio"]),
    ("andres-felipe-reyes",      ["reyes"],               ["andres", "felipe"]),
    ("miguel-puentes-escamilla", ["puentes"],             ["miguel"]),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def norm(s: str) -> str:
    return unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()

def clean_val(s: str | None) -> str | None:
    if not s:
        return None
    s = s.strip().strip("-").strip()
    return s if s and s not in {"N/A", "n/a", "NA", "-", "."} else None


def sanitize_doi(raw: str | None) -> str | None:
    if not raw:
        return None
    s = raw.strip()
    # Strip common URL prefixes
    for prefix in ("https://doi.org/", "http://doi.org/",
                   "https://dx.doi.org/", "http://dx.doi.org/"):
        if s.lower().startswith(prefix):
            s = s[len(prefix):]
            break
    # Strip "doi:" literal prefix
    if s.lower().startswith("doi:"):
        s = s[4:]
    s = s.strip()
    return s if s and s not in {"N/A", "NA", "-", ""} else None

def make_slug(authors: list[str], year: int, title: str) -> str:
    last = re.sub(r"\W+", "", norm(authors[0].split()[-1])) if authors else "unknown"
    word = re.sub(r"\W+", "", norm(title.split()[0])) if title.split() else "pub"
    return f"{last}{year}_{word[:20]}"

def detect_internal(author: str) -> str | None:
    parts = set(norm(author).split())
    for slug, lastnames, firstnames in RESEARCHERS:
        if any(ln in parts for ln in lastnames) and any(fn in parts for fn in firstnames):
            return slug
    return None

def yaml_str(s: str | None) -> str:
    if not s:
        return '""'
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'

# ── CSV parsing ───────────────────────────────────────────────────────────────

def parse_article_meta(meta: str) -> dict:
    """Extract journal, volume, issue, pages, doi from article metadata line."""
    doi_m = re.search(r"\bDOI:\s*([^\s,;]+)", meta, re.IGNORECASE)
    doi   = sanitize_doi(doi_m.group(1)) if doi_m else None

    # Journal name precedes "ISSN:"
    j_m = re.search(r"([A-ZÁÉÍÓÚÑA-Z][A-Za-záéíóúñüÜ\s\-&]+?)\s+ISSN:", meta)
    journal = j_m.group(1).strip().title() if j_m else None

    vol_m   = re.search(r"\bvol:\s*(\S+)",   meta, re.IGNORECASE)
    fasc_m  = re.search(r"\bfasc:\s*(\S+)",  meta, re.IGNORECASE)
    pags_m  = re.search(r"\bpágs?:\s*([\d]+\s*-\s*[\d]+)", meta, re.IGNORECASE)

    volume = clean_val(vol_m.group(1).rstrip(","))   if vol_m  else None
    issue  = clean_val(fasc_m.group(1).rstrip(","))  if fasc_m else None
    pages  = pags_m.group(1).replace(" ", "")        if pags_m else None

    return {"doi": doi, "journal": journal, "volume": volume,
            "issue": issue, "pages": pages}


def parse_book_meta(meta: str) -> dict:
    """Extract publisher, isbn, doi from book/chapter metadata line."""
    doi_m  = re.search(r"\bDOI:\s*([^\s,;]+)", meta, re.IGNORECASE)
    isbn_m = re.search(r"\bISBN:\s*([\w\-]+)",  meta, re.IGNORECASE)
    pub_m  = re.search(r"\bEd\.\s*([^,\n]+)",   meta, re.IGNORECASE)

    doi       = sanitize_doi(doi_m.group(1))                 if doi_m  else None
    publisher = clean_val(pub_m.group(1).strip())            if pub_m  else None

    return {"doi": doi, "journal": publisher, "isbn": isbn_m.group(1) if isbn_m else None,
            "volume": None, "issue": None, "pages": None}


def parse_preprint_meta(meta: str) -> dict:
    """Extract doi, url from working-paper metadata line."""
    doi_m = re.search(r"\bDOI:\s*([^\s,;]+)", meta, re.IGNORECASE)
    url_m = re.search(r"\bURL:\s*(\S+)",       meta, re.IGNORECASE)
    doi   = sanitize_doi(doi_m.group(1)) if doi_m else None
    url   = clean_val(url_m.group(1)) if url_m else None
    return {"doi": doi, "url": url, "journal": None,
            "volume": None, "issue": None, "pages": None}


def titlecase_name(raw: str) -> str:
    """'JUAN DAVID LEONGOMEZ PENA' → 'Juan David Leongomez Pena'"""
    return " ".join(w.capitalize() for w in raw.split())


def parse_entry(text: str, section_type: str) -> dict | None:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return None

    # Line 0: "N.- TypeLabel : Title"
    first = re.sub(r"^\d+\.-\s*", "", lines[0])
    m = re.match(r"(.+?)\s*:\s*(.+)", first, re.DOTALL)
    if not m:
        return None
    title = m.group(2).strip()

    # Separate "Autores:" line from metadata
    authors_raw = ""
    meta_lines: list[str] = []
    for line in lines[1:]:
        if line.startswith("Autores:"):
            authors_raw = line[len("Autores:"):].strip()
        else:
            meta_lines.append(line)
    meta = " ".join(meta_lines)

    # Year
    y_m = re.search(r"\b(20\d{2}|199\d)\b", meta)
    if not y_m:
        y_m = re.search(r"\b(20\d{2}|199\d)\b", first)
    year = int(y_m.group(1)) if y_m else 0
    if year < YEAR_MIN or year > YEAR_MAX:
        return None

    # Type-specific metadata
    if section_type == "article":
        meta_fields = parse_article_meta(meta)
    elif section_type == "preprint":
        meta_fields = parse_preprint_meta(meta)
    else:  # book, book-chapter, other
        meta_fields = parse_book_meta(meta)

    # Authors
    authors: list[str] = []
    for raw in authors_raw.split(","):
        raw = raw.strip()
        if raw:
            authors.append(titlecase_name(raw))

    internal = [s for a in authors if (s := detect_internal(a))]

    pub: dict = {
        "title":            title,
        "year":             year,
        "authors":          authors,
        "internal_authors": internal,
        "pub_type":         section_type,
        "doi":              meta_fields.get("doi"),
        "journal":          meta_fields.get("journal"),
        "volume":           meta_fields.get("volume"),
        "issue":            meta_fields.get("issue"),
        "pages":            meta_fields.get("pages"),
        "preprint_url":     meta_fields.get("url"),
        "abstract":         None,
    }
    return pub


def load_csv_dir() -> list[dict]:
    """Read all CSV files in CSV_DIR and return a list of raw publication dicts."""
    pubs: list[dict] = []
    for fname, section_type in FILE_TYPE.items():
        path = CSV_DIR / fname
        if not path.exists():
            print(f"  [SKIP] {fname} not found", file=sys.stderr)
            continue
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
        # First row is the section heading (skip); each subsequent row is one entry
        for row in rows[1:]:
            if not row:
                continue
            text = row[0]
            pub = parse_entry(text, section_type)
            if pub:
                pubs.append(pub)
    return pubs


# ── Enrichment ────────────────────────────────────────────────────────────────

def enrich_crossref(pub: dict) -> None:
    """Overwrite authors, title, journal, vol, issue, pages, abstract from Crossref."""
    doi = pub.get("doi")
    if not doi:
        return
    try:
        r = requests.get(
            f"https://api.crossref.org/works/{doi}",
            headers=HEADERS, timeout=15,
        )
        if r.status_code != 200:
            return
        item = r.json().get("message", {})
    except Exception:
        return

    # Authors
    raw_authors = item.get("author", [])
    if raw_authors:
        names = []
        for a in raw_authors:
            given  = a.get("given", "").strip()
            family = a.get("family", "").strip()
            names.append(f"{given} {family}".strip() if given else family)
        if names:
            pub["authors"] = names
            pub["internal_authors"] = [s for a in names if (s := detect_internal(a))]

    # Title
    titles = item.get("title", [])
    if titles:
        pub["title"] = titles[0]

    # Journal — strip trailing volume number some publishers embed in container-title
    container = item.get("container-title", [])
    if container:
        j = re.sub(r"[\s,]+\d+$", "", container[0]).strip()
        pub["journal"] = j

    # Volume / issue / pages
    if v := item.get("volume"):
        pub["volume"] = str(v)
    if i := item.get("issue"):
        pub["issue"] = str(i)
    if p := item.get("page"):
        pub["pages"] = p

    # Year (from issued date, more reliable)
    dp = item.get("issued", {}).get("date-parts", [[]])
    if dp and dp[0]:
        pub["year"] = dp[0][0]

    # Abstract (strip JATS tags)
    if ab := item.get("abstract"):
        pub["abstract"] = re.sub(r"<[^>]+>", "", ab).strip()


def enrich_semantic_scholar(pub: dict) -> None:
    """Fetch abstract from Semantic Scholar if still missing."""
    doi = pub.get("doi")
    if not doi or pub.get("abstract"):
        return
    try:
        r = requests.get(
            f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}",
            params={"fields": "abstract"},
            headers=HEADERS, timeout=15,
        )
        if r.status_code != 200:
            return
        if ab := r.json().get("abstract"):
            pub["abstract"] = ab
    except Exception:
        return


# ── Output ────────────────────────────────────────────────────────────────────

def write_md(pub: dict, out_path: Path) -> None:
    lines = ["---"]
    lines.append(f"title: {yaml_str(pub['title'])}")
    lines.append(f"year: {pub['year']}")

    lines.append("authors:")
    for a in pub["authors"]:
        lines.append(f"  - {yaml_str(a)}")

    if pub["internal_authors"]:
        lines.append("internal_authors:")
        for s in pub["internal_authors"]:
            lines.append(f"  - {s}")

    if pub.get("doi"):
        lines.append(f"doi: {yaml_str(pub['doi'])}")
    if pub.get("journal"):
        lines.append(f"journal: {yaml_str(pub['journal'])}")
    if pub.get("volume"):
        lines.append(f"volume: {yaml_str(pub['volume'])}")
    if pub.get("issue"):
        lines.append(f"issue: {yaml_str(pub['issue'])}")
    if pub.get("pages"):
        lines.append(f"pages: {yaml_str(pub['pages'])}")
    pu = pub.get("preprint_url") or ""
    if pu.startswith("http"):
        lines.append(f"preprint: {yaml_str(pu)}")
    if pub.get("abstract"):
        lines.append(f"abstract: {yaml_str(pub['abstract'])}")
    lines.append(f"pub_type: {pub['pub_type']}")
    lines.append("featured: false")
    lines.append("---")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"Reading CSV files from {CSV_DIR} …")
    raw = load_csv_dir()
    print(f"  {len(raw)} entries parsed in range {YEAR_MIN}–{YEAR_MAX}")

    # Deduplicate: DOI wins; else normalized title
    seen_dois:   set[str] = set()
    seen_titles: set[str] = set()
    pubs: list[dict] = []
    for p in raw:
        doi = (p.get("doi") or "").strip().lower()
        nt  = norm(p["title"])
        if doi and doi in seen_dois:
            continue
        if nt in seen_titles:
            continue
        if doi:
            seen_dois.add(doi)
        seen_titles.add(nt)
        pubs.append(p)

    print(f"  {len(pubs)} unique after deduplication")

    # Skip entries already in the output directory
    existing_dois: set[str] = set()
    existing_titles: set[str] = set()
    for md in OUTPUT_DIR.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        dm = re.search(r'^doi:\s*"?([^"\n]+)"?', text, re.MULTILINE)
        if dm:
            existing_dois.add(dm.group(1).strip().lower())
        tm = re.search(r'^title:\s*"?([^"\n]+)"?', text, re.MULTILINE)
        if tm:
            existing_titles.add(norm(tm.group(1).strip()))

    new_pubs = []
    skipped  = 0
    for p in pubs:
        doi = (p.get("doi") or "").strip().lower()
        nt  = norm(p["title"])
        if (doi and doi in existing_dois) or nt in existing_titles:
            skipped += 1
        else:
            new_pubs.append(p)

    print(f"  {skipped} already exist — will import {len(new_pubs)} new entries")

    # Enrich
    if not NO_ENRICH:
        need_enrich = [p for p in new_pubs if p.get("doi")]
        print(f"\nEnriching {len(need_enrich)} entries with DOIs via Crossref …")
        for i, p in enumerate(need_enrich, 1):
            enrich_crossref(p)
            time.sleep(REQUEST_DELAY)
            if i % 10 == 0:
                print(f"  {i}/{len(need_enrich)}")
        print("Filling missing abstracts via Semantic Scholar …")
        need_s2 = [p for p in new_pubs if p.get("doi") and not p.get("abstract")]
        for i, p in enumerate(need_s2, 1):
            enrich_semantic_scholar(p)
            time.sleep(REQUEST_DELAY)
            if i % 10 == 0:
                print(f"  {i}/{len(need_s2)}")

    # Generate slugs, handle collisions
    slug_counts: dict[str, int] = {}
    for p in new_pubs:
        base = make_slug(p["authors"], p["year"], p["title"])
        slug_counts[base] = slug_counts.get(base, 0) + 1

    slug_used: dict[str, int] = {}
    for p in new_pubs:
        base = make_slug(p["authors"], p["year"], p["title"])
        n = slug_counts[base]
        if n > 1:
            idx = slug_used.get(base, 0) + 1
            slug_used[base] = idx
            p["_slug"] = f"{base}_{idx}"
        else:
            p["_slug"] = base

    # Write
    if DRY_RUN:
        print("\n── DRY RUN — no files written ──────────────────────────────────")
        for p in sorted(new_pubs, key=lambda x: -x["year"]):
            doi_str = p.get("doi") or "NO DOI"
            ab_str  = "abstract" if p.get("abstract") else "no-abstract"
            int_str = ",".join(p["internal_authors"]) or "—"
            print(f"  {p['year']} | {p['pub_type']:12} | {doi_str[:30]:32} | {ab_str} | {int_str} | {p['title'][:55]}")
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        written = 0
        for p in new_pubs:
            out_path = OUTPUT_DIR / f"{p['_slug']}.md"
            if out_path.exists():
                # Avoid overwriting manually edited files
                stem = p["_slug"] + "_import"
                out_path = OUTPUT_DIR / f"{stem}.md"
            write_md(p, out_path)
            written += 1

        print(f"\n✅  {written} files written to {OUTPUT_DIR}")

    # Summary
    from collections import Counter
    by_type = Counter(p["pub_type"] for p in new_pubs)
    no_doi      = sum(1 for p in new_pubs if not p.get("doi"))
    no_abstract = sum(1 for p in new_pubs if not p.get("abstract"))
    no_internal = sum(1 for p in new_pubs if not p["internal_authors"])

    print(f"\n── Summary ──────────────────────────────────────────────────────")
    for t, n in sorted(by_type.items()):
        print(f"  {t:15} {n:3}")
    print(f"  {'no DOI':15} {no_doi:3}")
    print(f"  {'no abstract':15} {no_abstract:3}")
    print(f"  {'no internal auth':15} {no_internal:3}")


if __name__ == "__main__":
    main()
