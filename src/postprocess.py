import csv
import html as html_lib
import os
import re

DET_RE = re.compile(r"<\|det\|>[^<\s]*\s*(?:\[[^\]]*\])?\s*<\|/det\|>")
PAGE_MARKER_RE = re.compile(r"^---\s*Page\s+(\d+)\s*---\s*$", re.M)


def split_pages(text):
    marks = list(PAGE_MARKER_RE.finditer(text))
    if not marks:
        return [text]
    pages = []
    for i, mark in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        pages.append(text[mark.end():end].strip("\n"))
    return pages


def strip_det(text):
    return DET_RE.sub("", text)


def _cell_text(cell):
    return html_lib.unescape(re.sub(r"<[^>]+>", "", cell)).strip()


def extract_html_tables(text):
    tables = []
    for tbl in re.findall(r"<table>.*?</table>", text, flags=re.S | re.I):
        rows = []
        for tr in re.findall(r"<tr>(.*?)</tr>", tbl, flags=re.S | re.I):
            cells = [_cell_text(td) for td in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.S | re.I)]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def write_tables_csv(tables, out_dir, base_name):
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for i, rows in enumerate(tables, start=1):
        name = f"{base_name}_tabla{i}.csv" if len(tables) > 1 else f"{base_name}_tabla.csv"
        path = os.path.join(out_dir, name)
        width = max(len(r) for r in rows)
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row + [""] * (width - len(row)))
        paths.append(path)
    return paths


def html_table_to_md(html):
    out = []
    for tbl in re.findall(r"<table>.*?</table>", html, flags=re.S | re.I):
        rows = []
        for tr in re.findall(r"<tr>(.*?)</tr>", tbl, flags=re.S | re.I):
            cells = [_cell_text(td) for td in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.S | re.I)]
            if cells:
                rows.append(cells)
        if not rows:
            continue
        width = max(len(r) for r in rows) if rows else 0
        rows = [r + [""] * (width - len(r)) for r in rows]
        out.append(
            "| " + " | ".join(rows[0]) + " |\n"
            + "| " + " | ".join(["---"] * width) + " |\n"
            + "\n".join("| " + " | ".join(r) + " |" for r in rows[1:])
        )
    return "\n\n".join(out)


def to_markdown(raw):
    text = strip_det(raw)
    if "<table" not in text.lower():
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
    md = html_table_to_md(text)
    if md:
        parts = re.split(r"<table>.*?</table>", text, flags=re.S | re.I)
        result = parts[0].strip()
        md_parts = md.split("\n\n")
        for chunk in parts[1:]:
            if md_parts:
                result += "\n\n" + md_parts.pop(0) + "\n\n" + chunk.strip()
            else:
                result += "\n\n" + chunk.strip()
        text = result
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
