<h1 align="center">Read Document with UnlimitedOCR</h1>

<p align="center">
  <img src="https://img.shields.io/github/license/fabianperdomolaguna/Local_OCR_Parser_Unlimited-OCR?style=for-the-badge" alt="alt text">
  <img src="https://img.shields.io/badge/Python-3.13-FFFF00?style=for-the-badge&logo=Python&logoColor=white" alt="alt text">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit Badge"/>
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama Badge"/>
</p>

---

This project is a streamlit app that bridge [Unlimited-OCR](https://github.com/baidu/Unlimited-OCR) to read and parse a document into a markdown file in a local environment.  Features live OCR preview, automatic saving of raw OCR, Markdown (Python parser), and per-table CSVs. Uses Ollama for local LLM structuring. Output files preserved complete even when screen shows only the first page.

---

## ✨ Features
- **🎯 Precise OCR**: Uses Baidu's Unlimited-OCR model for detailed document transcription.
- **🧠 Local LLM Structuring**: Post-processes raw OCR outputs locally with Ollama (configured to use fast models like `llama3.2:1b` with `think=false`).
- **🎛️ Streamlit Dashboard**: A native Web UI featuring a side-by-side layout, image visualization, and instant status monitoring.
- **📝 Automated Output saving**: Writes the raw OCR, the Markdown and one CSV per table into `output/` on every run. The on-screen result shows only the first page of multi-page PDFs; the saved files keep the whole document.

---

## 🛠️ Dependencies
- **[UV](https://docs.astral.sh/uv/):** como gestor de dependencia
- **[Unlimited-OCR](https://github.com/baidu/Unlimited-OCR):** in a local environment
- **Core Engine**: `gradio_client` (Baidu Space connection)
- **Structuring**: `ollama` (Official Python SDK client)
- **Frontend**: `streamlit` (UI rendering)
- **Image handling**: `pillow` (mock receipt builder)

---

## 🚀 Setup & Launch

### 1. Install Unlimited-OCR in local using Docker
```powershell
# For Linux install first the Nvidia Container Toolkit
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
docker run -it -p 7860:7860 --platform=linux/amd64 --gpus all \
	registry.hf.space/baidu-unlimited-ocr:latest python app.py
```

### 2. Install Dependencies
```powershell
uv sync
```

### 3. Verify local Ollama is Running
Make sure the local Ollama server is running and the model is downloaded (Ollama post-processing is optional):

```powershell
ollama run llama3.2:1b
```

### 3. Launch App
```powershell
uv run streamlit run src/main.py
```

---

## 📂 File Architecture
```bash
📂 Unlimited OCR
 ├── 📄 src/
 │   ├── main.py            # Entry point (streamlit run src/main.py)
 │   ├── ui.py              # Streamlit interface (sidebar, upload, live OCR box, results)
 │   ├── ocr.py             # Unlimited-OCR (Gradio) + Ollama calls
 │   └── postprocess.py     # HTML tables -> Markdown / CSV
 ├── 📄 output/             # Results saved on every run (txt, md, csv)
 ├── 📄 pyproject.toml      # Dependencies
 └── 📄 README.md           # System documentation
```

---

## 💡 Real-world Use Cases

<details>
<summary><b>📋 1. Invoice & Receipt Parsing</b></summary>
Automatically extracts financial receipts, totals, tax, server, and quantities directly into a searchable database.
</details>

<details>
<summary><b>📚 2. Academic & Multi-column Parsing</b></summary>
Handles complex layouts (multi-column text, annotations, footers) and structures them sequentially.
</details>

<details>
<summary><b>🏥 3. Medical Report Structuring</b></summary>
Parses unstructured legacy lab results and scanning logs into standard clinical reports.
</details>

<details>
<summary><b>📦 4. Logistics & Manifest Auditing</b></summary>
Converts raw warehouse logs, shipping slips, and packaging details into auditable cargo manifests.
</details>

<details>
<summary><b>🏛️ 5. Historical Archive Search</b></summary>
Processes old print archive scans, cleaning up syntax anomalies and archaic spelling via the local LLM.
</details>

## 🏷️ Keywords
`Unlimited-OCR`, `Ollama`, `Local LLM OCR`, `Streamlit OCR`, `Free Document Parsing`, `Python OCR Pipeline`, `Gradio Client OCR`
