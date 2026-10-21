import os
import tempfile
import pymupdf
from gradio_client import Client, handle_file

OCR_URL = "http://127.0.0.1:7860"


def run_ocr(path, mode, ocr_prompt, on_text=None, page=None, total=None):
    text = ""
    try:
        client = Client(OCR_URL)
        job = client.submit(handle_file(path), mode, ocr_prompt, api_name="/run_ocr")
        for out in job:
            text = out.get("text", "") if isinstance(out, dict) else str(out)
            if text and on_text:
                on_text(text, page, total)
        job.result()
        return text
    except Exception as e:
        return f"{text}\n\nOCR Failed: {e}".strip()


def pdf_to_images(pdf_path, out_dir):
    doc = pymupdf.open(pdf_path)
    paths = []
    for i, page in enumerate(doc):
        out = os.path.join(out_dir, f"page_{i + 1}.png")
        page.get_pixmap(matrix=pymupdf.Matrix(200 / 72, 200 / 72)).save(out)
        paths.append(out)
    doc.close()
    return paths


def ocr_file(path, mode, ocr_prompt, on_text=None):
    if not path.lower().endswith(".pdf"):
        return run_ocr(path, mode, ocr_prompt, on_text, page=1, total=1)
    out_dir = tempfile.mkdtemp(prefix="pdf_ocr_")
    pages = pdf_to_images(path, out_dir)
    total = len(pages)
    full = ""
    for i, page in enumerate(pages, start=1):
        full += f"--- Page {i} ---\n"
        acc = full

        def make_cb(prefix):
            def cb(t, page_no=i, page_total=total):
                if on_text:
                    on_text(prefix + t, page_no, page_total)
            return cb

        page_text = run_ocr(page, mode, ocr_prompt, make_cb(acc))
        full += page_text
    if on_text:
        on_text(full, total, total)
    return full


def run_ollama(text, system_msg, user_prompt, model="llama3.2:1b"):
    try:
        import ollama
        import re
        prompt = user_prompt.replace("{text}", text)
        res = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            options={"temperature": 0.0}
        )
        content = res.message.content
        return re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    except Exception as e:
        return f"Ollama Error: {e}"
