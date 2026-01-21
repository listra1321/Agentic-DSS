import streamlit as st
import os
import json
import requests

# ======================================================
# Page Config
# ======================================================
st.set_page_config(
    page_title="Agentic DSS Ekowisata",
    layout="wide"
)

# ======================================================
# OpenRouter Config
# ======================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    st.error("OPENROUTER_API_KEY belum diset di Streamlit Secrets.")
    st.stop()

# ======================================================
# Utility Functions
# ======================================================
def load_jsonl(path, limit=3):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            data.append(json.loads(line))
    return data

def build_context_from_input(data):
    return "\n".join(item["input"] for item in data if "input" in item)

# ======================================================
# Load Dataset
# ======================================================
DATA_PATH = "db_listra.jsonl"

if not os.path.exists(DATA_PATH):
    st.error("Dataset db_listra.jsonl tidak ditemukan.")
    st.stop()

dataset_sample = load_jsonl(DATA_PATH)
context_data = build_context_from_input(dataset_sample)

# ======================================================
# UI
# ======================================================
st.title("🌿 Agentic Decision Support System (DSS) Ekowisata")

with st.expander("🔍 Contoh Data Ulasan Wisatawan"):
    st.json(dataset_sample)

destinasi = st.text_input("Nama Destinasi Wisata", "Danau Toba")

tujuan_kebijakan = st.selectbox(
    "Tujuan Kebijakan",
    [
        "Konservasi Lingkungan",
        "Pemberdayaan Masyarakat Lokal",
        "Optimalisasi Ekonomi Pariwisata",
        "Keseimbangan Ekowisata Berkelanjutan"
    ]
)

# ======================================================
# DSS Inference
# ======================================================
if st.button("🧠 Generate Storytelling & Rekomendasi Kebijakan"):
    with st.spinner("Melakukan penalaran kebijakan..."):

        prompt = f"""
Anda adalah sistem pendukung keputusan kebijakan ekowisata berkelanjutan.

Data ulasan wisatawan:
{context_data}

Destinasi: {destinasi}
Tujuan kebijakan: {tujuan_kebijakan}

Tugas:
1. Buat storytelling kebijakan yang reflektif.
2. Identifikasi isu utama.
3. Berikan 3 rekomendasi kebijakan konkret.
"""

        payload = {
            "model": "meta-llama/llama-3.2-3b-instruct",
            "messages": [
                {"role": "system", "content": "Anda adalah DSS kebijakan ekowisata."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            st.error(response.text)
            st.stop()

        hasil = response.json()["choices"][0]["message"]["content"]

    st.subheader("📄 Storytelling Kebijakan & Rekomendasi DSS")
    st.write(hasil)

st.markdown("---")
st.caption(
    "Prototipe DSS berbasis agentic storytelling untuk kebijakan ekowisata."
)
