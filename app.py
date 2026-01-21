import streamlit as st
import os
import json
import requests

# ======================================================
# Streamlit Page Config
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
    texts = []
    for item in data:
        if "input" in item:
            texts.append(item["input"])
    return "\n".join(texts)

# ======================================================
# Load Dataset (SAMA DENGAN KODE PROF)
# ======================================================
DATA_PATH = "db_listra.jsonl"

if not os.path.exists(DATA_PATH):
    st.error("Dataset db_listra.jsonl tidak ditemukan.")
    st.stop()

dataset_sample = load_jsonl(DATA_PATH, limit=3)
context_data = build_context_from_input(dataset_sample)

# ======================================================
# UI (SAMA DENGAN KODE PROF)
# ======================================================
st.title("🌿 Agentic Decision Support System (DSS) Ekowisata")
st.markdown(
    "Prototipe sistem pendukung keputusan berbasis **storytelling multimodal** "
    "untuk mendukung kebijakan ekowisata berkelanjutan."
)

with st.expander("🔍 Contoh Data Ulasan Wisatawan (JSONL)"):
    st.json(dataset_sample)

st.subheader("📥 Konteks Pengambilan Keputusan Kebijakan")

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
# DSS Inference (LOGIKA PROF, API DIGANTI)
# ======================================================
if st.button("🧠 Generate Storytelling & Rekomendasi Kebijakan"):
    with st.spinner("Melakukan penalaran kebijakan berbasis storytelling..."):

        prompt = f"""
Anda adalah sistem pendukung keputusan kebijakan ekowisata berkelanjutan.

Berikut adalah data ulasan wisatawan yang merepresentasikan kondisi lapangan:
{context_data}

Destinasi: {destinasi}
Tujuan kebijakan: {tujuan_kebijakan}

Tugas Anda:
1. Susun storytelling kebijakan wisata yang runtut, alami, dan reflektif berdasarkan data di atas.
2. Identifikasi isu utama yang muncul dari pengalaman pengunjung.
3. Berikan 3 rekomendasi kebijakan konkret dan aplikatif.

Gunakan bahasa formal kebijakan, namun tetap naratif dan mudah dipahami.
"""

        payload = {
            "model": "meta-llama/llama-3.2-3b-instruct",
            "messages": [
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
    "Catatan: Sistem ini merupakan prototipe DSS berbasis agentic control "
    "dan tidak menggantikan kewenangan pengambil kebijakan."
)
