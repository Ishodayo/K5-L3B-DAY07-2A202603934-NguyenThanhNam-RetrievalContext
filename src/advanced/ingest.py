"""Ingest WHO World health statistics 2023 into chunks of three kinds, all traceable to a PDF page.

text   : paragraphs from the PDF text layer (pymupdf), <= MAX_CHARS, never crossing a page
table  : Annex 1 statistical tables, one chunk per country/region row per annex part; the left page
         (with country names) and the right page (more indicators, same row order) are joined
visual : a Gemini vision transcription of every page that holds figures, charts, maps or diagrams
         (title, type, axes/units, legend, printed values, notes); the page image is rendered at
         VISION_DPI and can be regenerated with `adv-render`. Model output is cached in
         data/advanced/vision.json and must be checked against the original (it can be wrong).

Page numbers: `page` = PDF page (1-based); `printed_page` = PDF page - 12 for numbered pages.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from .. import config

DOC_ID = "who_whs2023"
PDF_PATH = config.ROOT / "starter" / "data" / "advanced" / "9789240074323-eng.pdf"
ADV_DIR = config.ROOT / "data" / "advanced"
CHUNKS_OUT = ADV_DIR / "chunks.json"
VISION_CACHE = ADV_DIR / "vision.json"
RENDER_DIR = config.ROOT / "starter" / "data" / "advanced" / "pages"
SOURCE = {
    "source_id": DOC_ID,
    "title": "World health statistics 2023: monitoring health for the SDGs, sustainable development goals",
    "publisher": "World Health Organization", "year": 2023, "isbn": "9789240074323",
    "url": "https://www.who.int/publications/i/item/9789240074323",
    "license": "CC BY-NC-SA 3.0 IGO",
    "pdf_sha256": "26292b8da46851a146e02861356fded41fc408f65597b9ec18d4fcd94d9b6674",
    "pdf_pages": 136, "printed_pages": 119, "accessed_at": "2026-11-16",
}
PRINTED_OFFSET = 12
MAX_CHARS = 1400
VISION_DPI = 150
ANNEX_PAIRS = [(96, 97), (98, 99), (100, 101), (102, 103), (104, 105), (106, 107), (108, 109), (110, 111),
               (112, 113), (114, 115), (116, 117), (118, 119), (120, 121), (122, 123), (124, 125), (126, 127)]
ANNEX_PART = {96: "Annex 1-1", 104: "Annex 1-2", 112: "Annex 1-3", 120: "Annex 1-4"}
YEAR_RE = re.compile(r"^(19|20)\d\d(\s*[–-]\s*(19|20)\d\d)?$")


def _open():
    import pymupdf

    if not PDF_PATH.exists():
        raise FileNotFoundError(f"{PDF_PATH} missing: download the WHO PDF (see HOW_TO_RUN.md)")
    digest = hashlib.sha256(PDF_PATH.read_bytes()).hexdigest()
    if digest != SOURCE["pdf_sha256"]:
        raise RuntimeError(f"PDF sha256 {digest[:12]} != expected {SOURCE['pdf_sha256'][:12]}: different file")
    return pymupdf.open(PDF_PATH)


def _clean(s: str | None) -> str:
    return " ".join((s or "").split())


def _section_map(doc) -> dict[int, str]:
    toc = sorted((p, t.replace("\xa0", " ").strip()) for _, t, p in doc.get_toc())
    out, cur = {}, "Front matter"
    for page in range(1, doc.page_count + 1):
        for p, t in toc:
            if p == page:
                cur = t
        out[page] = cur
    return out


def _chunk(cid: str, page: int, kind: str, text: str, section: str, **meta) -> dict[str, Any]:
    printed = page - PRINTED_OFFSET if 13 <= page <= 131 else None
    return {"id": cid, "text": text, "source_id": DOC_ID, "source": SOURCE["url"], "page": page,
            "metadata": {"kind": kind, "printed_page": printed, "section": section,
                         "version": "2023", "pdf_sha256": SOURCE["pdf_sha256"], **meta}}


def text_chunks(doc, sections) -> list[dict[str, Any]]:
    annex_pages = {p for pair in ANNEX_PAIRS for p in pair}
    chunks = []
    for page in range(1, doc.page_count + 1):
        if page in annex_pages:
            continue
        blocks = [_clean(b[4]) for b in doc[page - 1].get_text("blocks") if b[6] == 0 and _clean(b[4])]
        buf, n = "", 0
        for b in blocks:
            if buf and len(buf) + len(b) + 1 > MAX_CHARS:
                chunks.append(_chunk(f"A:{DOC_ID}:p{page:03d}:t{n:02d}", page, "text", buf, sections[page]))
                buf, n = "", n + 1
            while len(b) > MAX_CHARS:  # very long block: cut at a sentence end
                cut = b.rfind(". ", 0, MAX_CHARS) + 1 or MAX_CHARS
                chunks.append(_chunk(f"A:{DOC_ID}:p{page:03d}:t{n:02d}", page, "text", b[:cut].strip(),
                                     sections[page]))
                b, n = b[cut:].strip(), n + 1
            buf = f"{buf} {b}".strip()
        if len(buf) >= 40:
            chunks.append(_chunk(f"A:{DOC_ID}:p{page:03d}:t{n:02d}", page, "text", buf, sections[page]))
    return chunks


def _split_header(rows: list[list[str]]) -> tuple[list[list[str]], list[list[str]]]:
    for i, r in enumerate(rows):
        if any(YEAR_RE.match(c) for c in r if c):
            return rows[:i + 1], rows[i + 1:]
    raise ValueError("no year row found in table header")


def _labels(header: list[list[str]], ncols: int, skip_first: bool) -> list[str]:
    filled = []
    for r in header:
        row, last = [], ""
        for c in r:
            last = c or last
            row.append(last)
        filled.append(row)
    labels = []
    for j in range(ncols):
        if skip_first and j == 0:
            labels.append("Country/area")
            continue
        parts = []
        for r in filled:
            v = r[j] if j < len(r) else ""
            if v and v not in parts and v not in ("Data type", "Countries and area", "Countries and areas"):
                parts.append(v)
        labels.append(" | ".join(parts))
    return labels


def table_chunks(doc) -> list[dict[str, Any]]:
    chunks, part = [], ""
    for left, right in ANNEX_PAIRS:
        part = ANNEX_PART.get(left, part)
        lt = doc[left - 1].find_tables().tables[0].extract()
        rt = doc[right - 1].find_tables().tables[0].extract()
        lt = [[_clean(c) for c in r] for r in lt]
        rt = [[_clean(c) for c in r] for r in rt]
        lh, ld = _split_header(lt)
        rh, rd = _split_header(rt)
        ld = [r for r in ld if r and r[0]]
        rd = [r for r in rd if any(r)]
        if len(ld) != len(rd):
            raise ValueError(f"p{left}/p{right}: {len(ld)} vs {len(rd)} data rows")
        llab, rlab = _labels(lh, len(lh[0]), True), _labels(rh, len(rh[0]), False)
        for i, (lr, rr) in enumerate(zip(ld, rd)):
            name = lr[0]
            cells = [f"{llab[j]}: {v}" for j, v in enumerate(lr) if j > 0 and v] + \
                    [f"{rlab[j]}: {v}" for j, v in enumerate(rr) if v]
            text = (f"{part} (WHO World health statistics 2023, PDF pages {left}-{right}, printed pages "
                    f"{left - PRINTED_OFFSET}-{right - PRINTED_OFFSET}) — {name}. '-' = no data.\n" + "\n".join(cells))
            chunks.append(_chunk(f"A:{DOC_ID}:p{left:03d}:r{i:02d}", left, "table", text,
                                 f"{part}. Country, area, WHO region and global health statistics",
                                 table=part, row=name, pages=[left, right]))
    return chunks


def visual_pages(doc) -> list[int]:
    out = []
    for page in range(14, 95):
        pg = doc[page - 1]
        text = _clean(pg.get_text())
        if len(text) < 100:
            continue  # chapter covers / blank
        draws, imgs = len(pg.get_drawings()), len(pg.get_images())
        if ("Figure" in text and draws >= 15) or imgs > 0 or draws >= 500:
            out.append(page)
    return out


VISION_PROMPT = """You are transcribing PDF page {page} (printed page {printed}) of the WHO report
"World health statistics 2023". For EVERY figure, chart, map, diagram, infographic, timeline or table
on this page, write a section:

## <Figure/Box number if printed>: <exact title>
- Type: (line chart, bar chart, stacked area, pie, map, diagram, timeline, table, ...)
- Axes / units / scale: ...
- Legend / series / colour categories: ...
- Values: list EVERY number printed on the figure (data labels, annotations, axis-end values) exactly as
  printed, each with what it refers to (series, region, year, category). For lines or bars WITHOUT printed
  values, give approximate values read from the axis at the first year, last year and turning points,
  marked with "≈".
- Maps: legend classes; regions/countries that are named or clearly identifiable in a class (only if sure).
- Diagrams/timelines: every box/event label with its year or position.
- Notes and source lines printed under the figure.
- What the figure shows: highest/lowest, direction of trends, comparisons that are directly visible.

Rules: use only what is visible on this page (no outside knowledge); copy numbers and names exactly;
write "unreadable" instead of guessing. Plain text, no preamble."""


def render(doc, page: int) -> Path:
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    path = RENDER_DIR / f"p{page:03d}.png"
    if not path.exists():
        doc[page - 1].get_pixmap(dpi=VISION_DPI).save(path)
    return path


def run_vision(doc, pages: list[int], model: str) -> dict[str, Any]:
    """Transcribe visual pages with Gemini; cached per page+model (paid API, see cost in the cache)."""
    from google import genai
    from google.genai import errors, types

    cache = json.loads(VISION_CACHE.read_text(encoding="utf-8")) if VISION_CACHE.exists() else {}
    client = genai.Client()
    for page in pages:
        key = f"p{page:03d}"
        if key in cache and cache[key]["model"] == model:
            continue
        img = render(doc, page).read_bytes()
        prompt = VISION_PROMPT.format(page=page, printed=page - PRINTED_OFFSET)
        t0, delay = time.perf_counter(), 5.0
        for attempt in range(5):
            try:
                resp = client.models.generate_content(
                    model=model, contents=[types.Part.from_bytes(data=img, mime_type="image/png"), prompt],
                    config=types.GenerateContentConfig(temperature=0))
                break
            except errors.APIError as exc:
                if attempt == 4 or getattr(exc, "code", None) not in (429, 500, 502, 503, 504):
                    raise
                time.sleep(delay)
                delay *= 2
        u = resp.usage_metadata
        cache[key] = {"page": page, "model": model, "dpi": VISION_DPI, "text": (resp.text or "").strip(),
                      "tokens": {"input": u.prompt_token_count or 0, "output": u.candidates_token_count or 0,
                                 "thoughts": getattr(u, "thoughts_token_count", 0) or 0},
                      "seconds": round(time.perf_counter() - t0, 1)}
        VISION_CACHE.parent.mkdir(parents=True, exist_ok=True)
        VISION_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"vision {key}: {len(cache[key]['text'])} chars, {cache[key]['seconds']} s")
    return cache


def visual_chunks(cache: dict[str, Any], sections) -> list[dict[str, Any]]:
    chunks = []
    for key in sorted(cache):
        v = cache[key]
        page = v["page"]
        parts = [p.strip() for p in re.split(r"\n(?=## )", v["text"]) if p.strip()]
        n = 0
        for part in parts:
            title = part.splitlines()[0].lstrip("# ").strip()
            body = part
            while body:
                piece, body = body[:MAX_CHARS], body[MAX_CHARS:]
                if body:  # keep the figure title on every piece
                    cut = piece.rfind("\n")
                    if cut > MAX_CHARS // 2:
                        body, piece = piece[cut:] + body, piece[:cut]
                    body = f"## {title} (continued)\n" + body.lstrip()
                text = (f"[Visual transcription of PDF page {page} (printed page {page - PRINTED_OFFSET}) by "
                        f"{v['model']}]\n{piece.strip()}")
                chunks.append(_chunk(f"A:{DOC_ID}:p{page:03d}:v{n:02d}", page, "visual", text, sections[page],
                                     figure=title, vision_model=v["model"], render_dpi=v["dpi"]))
                n += 1
    return chunks


def build(vision_model: str | None = None) -> dict[str, Any]:
    doc = _open()
    sections = _section_map(doc)
    pages = visual_pages(doc)
    cache = run_vision(doc, pages, vision_model or os.environ.get("GEMINI_MODEL", "")) if vision_model != "skip" \
        else (json.loads(VISION_CACHE.read_text(encoding="utf-8")) if VISION_CACHE.exists() else {})
    chunks = text_chunks(doc, sections) + table_chunks(doc) + visual_chunks(cache, sections)
    if len({c["id"] for c in chunks}) != len(chunks):
        raise ValueError("duplicate chunk ids")
    ADV_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_OUT.write_text(json.dumps(chunks, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (ADV_DIR / "source.json").write_text(json.dumps({**SOURCE, "visual_pages": pages}, ensure_ascii=False,
                                                    indent=2) + "\n", encoding="utf-8")
    kinds: dict[str, int] = {}
    for c in chunks:
        kinds[c["metadata"]["kind"]] = kinds.get(c["metadata"]["kind"], 0) + 1
    empty = [p for p in range(1, doc.page_count + 1) if len(_clean(doc[p - 1].get_text())) < 40]
    return {"chunks": len(chunks), "by_kind": kinds, "visual_pages": len(pages), "text_empty_pages": empty}
