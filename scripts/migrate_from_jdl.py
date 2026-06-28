#!/usr/bin/env python3
"""
Migra publicaciones del sitio personal Hugo Blox de Juan David Leongómez
al sitio CODEC en Astro.

Uso:
    python3 scripts/migrate_from_jdl.py
    python3 scripts/migrate_from_jdl.py --dry-run   # solo muestra, no escribe

Ejecutar desde la raíz del repositorio CODEC.
"""

import json
import re
import sys
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────────
JDL_SITE   = Path("/home/jdl/Documents/GitHub/JDL_website")
CODEC_PUBS = Path("src/content/publications")
LANG       = "es"

# ── Miembros de CODEC ──────────────────────────────────────────────────────────
# slug en sitio JDL → (nombre para mostrar, ID en CODEC)
CODEC_SLUGS = {
    "admin":           ("Juan David Leongómez",    "juan-david-leongomez"),
    "mva":             ("Milena Vásquez-Amézquita", "milena-vasquez-amezquita"),
    "ors":             ("Oscar R. Sánchez",          "oscar-sanchez"),
}

# Nombres que aparecen como strings (no como slugs) pero son de CODEC
CODEC_STRINGS = {
    "Mauricio Bonilla": ("Fidel Mauricio Bonilla", "fidel-mauricio-bonilla"),
    "Ana Maria Salazar": ("Ana María Salazar",     "ana-maria-salazar"),
}

# Slugs sin perfil en JDL: mapeo manual slug → nombre real
EXTRA_NAMES = {
    "chrisw": "Christopher D. Watkins",
}

# ── Mapeo de tipos de publicación ──────────────────────────────────────────────
PUB_TYPE_MAP = {
    "0": "other",
    "1": "conference",
    "2": "article",
    "3": "preprint",
    "4": "other",
    "5": "book",
    "6": "book-chapter",
}

# ── Carga de nombres de autores desde directorio JDL ──────────────────────────
def load_author_names(lang: str) -> dict:
    """Construye dict slug → nombre real leyendo los perfiles de autores."""
    names = {}
    authors_dir = JDL_SITE / "content" / lang / "authors"
    if not authors_dir.exists():
        return names
    for author_dir in sorted(authors_dir.iterdir()):
        if not author_dir.is_dir():
            continue
        index = author_dir / "_index.md"
        if not index.exists():
            continue
        text = index.read_text(encoding="utf-8")
        m = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
        if m:
            display = m.group(1).strip().strip("\"'")
            names[author_dir.name] = display
            names[author_dir.name.lower()] = display  # alias insensible a mayúsculas
    return names


# ── Parser de frontmatter TOML ─────────────────────────────────────────────────
def parse_toml_frontmatter(content: str) -> dict:
    m = re.match(r"^\+\+\+\n(.*?)\n\+\+\+", content, re.DOTALL)
    if not m:
        return {}
    toml = m.group(1)
    data = {}

    def get_str(key):
        # Double-quoted basic string (con escapes)
        m = re.search(rf'^{key}\s*=\s*"((?:[^"\\]|\\.)*)"', toml, re.MULTILINE)
        if m:
            return m.group(1).replace('\\"', '"').replace("\\n", " ")
        # Single-quoted literal string (sin escapes)
        m = re.search(rf"^{key}\s*=\s*'([^']*)'", toml, re.MULTILINE)
        return m.group(1) if m else None

    def get_bool(key):
        m = re.search(rf'^{key}\s*=\s*(true|false)', toml, re.MULTILINE)
        return (m.group(1) == "true") if m else False

    # Título
    t = get_str("title")
    if t:
        data["title"] = t

    # Año
    m = re.search(r"^date\s*=\s*(\d{4})", toml, re.MULTILINE)
    if m:
        data["year"] = int(m.group(1))

    # Autores (lista TOML)
    m = re.search(r"^authors\s*=\s*\[([^\]]+)\]", toml, re.MULTILINE | re.DOTALL)
    if m:
        data["authors"] = re.findall(r'"([^"]*)"', m.group(1))

    # Tipo
    m = re.search(r'^publication_types\s*=\s*\["(\d+)"\]', toml, re.MULTILINE)
    if m:
        data["pub_type_num"] = m.group(1)

    # Publicación (citación cruda)
    p = get_str("publication")
    if p:
        data["publication"] = p

    # DOI
    doi = get_str("doi")
    if doi:
        data["doi"] = doi

    # Abstract
    ab = get_str("abstract")
    if ab:
        data["abstract"] = ab

    # Featured
    data["featured"] = get_bool("featured")

    # URLs
    pdf = get_str("url_pdf")
    if pdf:
        data["pdf"] = pdf
    pre = get_str("url_preprint")
    if pre:
        data["preprint"] = pre

    return data


# ── Parser de citación Hugo Blox ───────────────────────────────────────────────
def parse_citation(pub: str) -> dict:
    """Convierte '*Revista, 10*(2), 1-15' en campos separados."""
    pub = pub.strip()

    # *Journal, Vol*(Issue), Pages
    m = re.match(r"\*([^,*]+),\s*(\d+)\*\((\d+)\),\s*(.+)", pub)
    if m:
        return dict(journal=m.group(1).strip(), volume=m.group(2),
                    issue=m.group(3), pages=m.group(4).strip())

    # *Journal, Vol*, Pages  (sin issue)
    m = re.match(r"\*([^,*]+),\s*(\d+)\*,\s*(.+)", pub)
    if m:
        return dict(journal=m.group(1).strip(), volume=m.group(2),
                    pages=m.group(3).strip())

    # *Journal* Vol(Issue), Pages
    m = re.match(r"\*([^*]+)\*\s+(\d+)\((\d+)\),\s*(.+)", pub)
    if m:
        return dict(journal=m.group(1).strip(), volume=m.group(2),
                    issue=m.group(3), pages=m.group(4).strip())

    # Solo *Journal*
    m = re.match(r"\*([^*]+)\*", pub)
    if m:
        return dict(journal=m.group(1).strip())

    return dict(journal=pub.replace("*", "").strip())


# ── Generador de YAML ──────────────────────────────────────────────────────────
def ys(s: str) -> str:
    """Serializa un string para YAML (usa JSON encoding, válido en YAML)."""
    return json.dumps(str(s), ensure_ascii=False)


def migrate_one(pub_dir: Path, author_names: dict) -> tuple[str | None, list]:
    """Convierte una publicación Hugo Blox a YAML frontmatter de CODEC.
    Devuelve (contenido_md, lista_de_advertencias)."""
    index = pub_dir / "index.md"
    if not index.exists():
        return None, []

    content = index.read_text(encoding="utf-8")
    data = parse_toml_frontmatter(content)
    if not data or "title" not in data:
        return None, ["sin frontmatter TOML"]

    warnings = []
    raw_authors = data.get("authors", [])
    display_authors = []
    internal_authors = []

    for a in raw_authors:
        if a in CODEC_SLUGS:
            name, rid = CODEC_SLUGS[a]
            display_authors.append(name)
            internal_authors.append(rid)
        elif a in CODEC_STRINGS:
            name, rid = CODEC_STRINGS[a]
            display_authors.append(name)
            internal_authors.append(rid)
        elif a in author_names or a.lower() in author_names:
            display_authors.append(author_names.get(a) or author_names[a.lower()])
        else:
            display_authors.append(a)
            # Avisar solo si parece un slug (ASCII puro, sin espacios ni puntos)
            try:
                a.encode("ascii")
                if " " not in a and "." not in a and "," not in a:
                    warnings.append(f"slug sin resolver: '{a}'")
            except UnicodeEncodeError:
                pass  # Nombre con caracteres no-ASCII → es un nombre real

    citation = parse_citation(data["publication"]) if "publication" in data else {}
    pub_type = PUB_TYPE_MAP.get(data.get("pub_type_num", "2"), "article")

    lines = ["---"]
    lines.append(f"title: {ys(data['title'])}")
    lines.append(f"year: {data.get('year', 2024)}")

    lines.append("authors:")
    for name in display_authors:
        lines.append(f"  - {ys(name)}")

    if internal_authors:
        lines.append("internal_authors:")
        for rid in internal_authors:
            lines.append(f"  - {rid}")

    if "doi" in data:
        lines.append(f"doi: {ys(data['doi'])}")

    if "journal" in citation:
        lines.append(f"journal: {ys(citation['journal'])}")
    if "volume" in citation:
        lines.append(f"volume: {ys(citation['volume'])}")
    if "issue" in citation:
        lines.append(f"issue: {ys(citation['issue'])}")
    if "pages" in citation:
        lines.append(f"pages: {ys(citation['pages'])}")

    lines.append(f"pub_type: {pub_type}")
    lines.append(f"featured: {'true' if data.get('featured') else 'false'}")

    if data.get("abstract"):
        lines.append(f"abstract: {ys(data['abstract'])}")

    if data.get("pdf"):
        lines.append(f"pdf: {ys(data['pdf'])}")
    if data.get("preprint"):
        lines.append(f"preprint: {ys(data['preprint'])}")

    lines.append("---")
    return "\n".join(lines) + "\n", warnings


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    dry_run = "--dry-run" in sys.argv

    print("Cargando nombres de autores...")
    author_names = load_author_names(LANG)
    # Agregar nombres de miembros CODEC al dict (para slugs internos)
    for slug, (name, _) in CODEC_SLUGS.items():
        author_names[slug] = name
    author_names.update(EXTRA_NAMES)
    print(f"  {len(author_names)} perfiles encontrados\n")

    pub_root = JDL_SITE / "content" / LANG / "publication"
    if not pub_root.exists():
        print(f"ERROR: no existe {pub_root}")
        sys.exit(1)

    if not dry_run:
        CODEC_PUBS.mkdir(parents=True, exist_ok=True)

    ok = skipped = errors = 0

    for pub_dir in sorted(pub_root.iterdir()):
        if not pub_dir.is_dir() or pub_dir.name.startswith("_"):
            continue

        slug = pub_dir.name.lower()
        out_file = CODEC_PUBS / f"{slug}.md"

        result, warns = migrate_one(pub_dir, author_names)

        if result is None:
            print(f"  ✗ SKIP  {pub_dir.name}")
            errors += 1
            continue

        status = "DRY " if dry_run else ("NEW " if not out_file.exists() else "UPD ")
        warn_str = f"  ⚠ {', '.join(warns)}" if warns else ""
        print(f"  {status}{slug}.md{warn_str}")

        if not dry_run:
            out_file.write_text(result, encoding="utf-8")
        ok += 1

    # Eliminar ejemplo placeholder si existe y hay pubs reales
    placeholder = CODEC_PUBS / "leongomez-2024-ejemplo.md"
    if ok > 0 and placeholder.exists() and not dry_run:
        placeholder.unlink()
        print(f"\n  (eliminado: leongomez-2024-ejemplo.md)")

    print(f"\n{'DRY RUN — ' if dry_run else ''}Resultado: {ok} migradas, {errors} con error")


if __name__ == "__main__":
    main()
