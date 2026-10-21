import os
import tempfile
import time
import html as html_lib
import streamlit as st
import streamlit.components.v1 as components
import pymupdf

from src.ocr import ocr_file, run_ollama
from src.postprocess import to_markdown, extract_html_tables, write_tables_csv, split_pages

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX_HEIGHT = 216
TAIL_CHARS = 4000  
REFRESH_EVERY = 0.3  


def render_sidebar():
    st.subheader("Settings")
    mode = st.selectbox("OCR Mode", ["gundam", "base"], help="gundam: fast (640px) | base: precise (1024px)")
    ocr_prompt = st.text_area("OCR Prompt", value="document parsing.", height=60)
    use_ollama = st.checkbox("Use Ollama for estructure/clean (optional)", value=False)
    system_msg = st.text_area(
        "Sistem message (Ollama)",
        "Directly output the final response in markdown. No <think> blocks or thoughts allowed.",
        height=80
    )
    user_prompt = st.text_area(
        "User Prompt (Ollama)",
        "Convert the OCR text into a clean Markdown.",
        height=100
    )
    return mode, ocr_prompt, use_ollama, system_msg, user_prompt


def render_upload():
    uploaded = st.file_uploader(
        "File to process (image or PDF)",
        type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff", "pdf"]
    )
    if uploaded is not None:
        if uploaded.name.lower().endswith(".pdf"):
            with pymupdf.open(stream=uploaded.getvalue(), filetype="pdf") as doc:
                st.caption(f"PDF: {doc.page_count} page(s)")
        else:
            st.image(uploaded, caption=uploaded.name, width=300)
    btn = st.button("Process Document", type="primary")
    return uploaded, btn


class OcrStream:

    def __init__(self):
        st.subheader("1. OCR (live)")
        self.box = st.empty()
        self.status = st.empty()
        self.page = None
        self.total = None
        self._last_render = 0.0

    def update(self, text, page=None, total=None, force=False):
        if page:
            self.page = page
        if total:
            self.total = total
        now = time.monotonic()
        if not force and now - self._last_render < REFRESH_EVERY:
            return
        self._last_render = now
        self._render(text)
        n_lines = text.count("\n") + 1 if text else 0
        page_txt = f"Page {self.page}/{self.total}" if self.page and self.total else ""
        self.status.caption(f"{page_txt} · {n_lines} lines · {len(text)} carachters".strip(" ·"))

    def _render(self, text):
        visible = text[-TAIL_CHARS:]
        prefix = "…\n" if len(text) > TAIL_CHARS else ""
        doc = f"""<style>body{{margin:0;background:transparent;}}</style>
                  <div id="ocr-box" style="height:{BOX_HEIGHT}px; overflow-y:auto; white-space:pre-wrap;
                  word-break:break-word; background:#0e1117; color:#e6edf3; padding:6px; border-radius:4px;
                  font-family:monospace; font-size:12px; line-height:18px;">
                    {html_lib.escape(prefix + visible)}
                  </div>
                  <script>
                    var el = document.getElementById('ocr-box');
                    el.scrollTop = el.scrollHeight;
                  </script>"""
        with self.box.container():
            components.html(doc, height=BOX_HEIGHT + 24)


def save_text(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def render_results(ocr_text, use_ollama, system_msg, user_prompt, doc_name, doc_output_dir):
    pages = split_pages(ocr_text)
    page1 = pages[0] if pages else ocr_text

    ocr_processed = None
    if not use_ollama:
        ocr_processed = to_markdown(ocr_text)

    ollama_result = None
    if use_ollama:
        ollama_result = run_ollama(ocr_text, system_msg, user_prompt)

    os.makedirs(doc_output_dir, exist_ok=True)
    saved = [save_text(os.path.join(doc_output_dir, f"{doc_name}_ocr_crudo.txt"), ocr_text)]

    if ocr_processed is not None:
        saved.append(save_text(os.path.join(doc_output_dir, f"{doc_name}_markdown_python.md"), ocr_processed))

    if ollama_result is not None:
        saved.append(save_text(os.path.join(doc_output_dir, f"{doc_name}_ollama.md"), ollama_result))

    tables = extract_html_tables(ocr_text)
    if tables:
        saved.extend(write_tables_csv(tables, doc_output_dir, doc_name))

    st.success("Saved on output/: " + ", ".join(os.path.basename(p) for p in saved))

    st.subheader("2. Result")
    if use_ollama:
        ollama_pages = split_pages(ollama_result)
        if len(ollama_pages) > 1:
            st.markdown(ollama_pages[0])
            st.caption(f"Showing just page 1 of {len(ollama_pages)} · the complete result is on {doc_name}_ollama.md")
        else:
            st.markdown(ollama_result)
    else:
        md_page1 = to_markdown(page1)
        st.markdown(md_page1 if md_page1 else page1)
        if len(pages) > 1:
            st.caption(f"Showing just page 1 of {len(pages)} · the complete document is on {doc_name}_markdown_python.md")
    return saved


def run_app():
    st.set_page_config(page_title="Unlimited OCR", page_icon="🔍", layout="wide")
    st.markdown("<h2 style='color:#ff8a00;'>🔍 Unlimited OCR</h2>", unsafe_allow_html=True)

    with st.sidebar:
        mode, ocr_prompt, use_ollama, system_msg, user_prompt = render_sidebar()

    col1, col2 = st.columns(2)
    with col1:
        uploaded, btn = render_upload()

    with col2:
        if btn:
            if uploaded is None:
                st.warning("Upload an image or a PDF to process it.")
            else:
                tmp_path = os.path.join(tempfile.gettempdir(), uploaded.name)
                with open(tmp_path, "wb") as f:
                    f.write(uploaded.getvalue())
                doc_name = os.path.splitext(uploaded.name)[0]
                doc_output_dir = os.path.join(PROJECT_ROOT, "output")

                stream = OcrStream()
                with st.spinner("Processing OCR..."):
                    ocr_text = ocr_file(tmp_path, mode, ocr_prompt, stream.update)
                stream.update(ocr_text, force=True)
                render_results(ocr_text, use_ollama, system_msg, user_prompt, doc_name, doc_output_dir)
