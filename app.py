import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# ======================================================
# Load environment variable
# ======================================================
load_dotenv()

# ======================================================
# OpenRouter Client
# ======================================================
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ======================================================
# Utility Functions
# ======================================================
def load_jsonl(path, limit=3):
    """Load JSONL dataset (limited for DSS inference)."""
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            data.append(json.loads(line))
    return data

def build_context_from_input(data):
    """Build context from 'input' field in dataset."""
    texts = []
    for item in data:
        if "input" in item:
            texts.append(item["input"])
    return "\n".join(texts)

# ======================================================
# Load Dataset
# ======================================================
DATA_PATH = "db_listra.jsonl"
dataset_sample = load_jsonl(DATA_PATH, limit=3)
context_data = build_context_from_input(dataset_sample)

# ======================================================
# Streamlit UI
# ======================================================
st.set_page_config(
    page_title="Agentic DSS Ekowisata",
    layout="wide"
)

st.title("🌿 Agentic Decision Support System (DSS) Ekowisata")
st.markdown(
    "Prototipe sistem pendukung keputusan berbasis **storytelling multimodal** "
    "untuk mendukung kebijakan ekowisata berkelanjutan."
)

# ======================================================
# Dataset Preview (Optional but recommended)
# ======================================================
with st.expander("🔍 Contoh Data Ulasan Wisatawan (JSONL)"):
    st.json(dataset_sample)

# ======================================================
# Policy Input
# ======================================================
st.subheader("📥 Konteks Pengambilan Keputusan Kebijakan")

destinasi = st.text_input(
    "Nama Destinasi Wisata",
    "Danau Toba"
)

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
3. Berikan 3 rekomendasi kebijakan konkret dan aplikatif untuk pengelolaan destinasi.

Gunakan bahasa formal kebijakan, namun tetap naratif dan mudah dipahami.
"""

        response = client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )

        hasil = response.choices[0].message.content

    # ==================================================
    # Output
    # ==================================================
    st.subheader("📄 Storytelling Kebijakan & Rekomendasi DSS")
    st.write(hasil)

# ======================================================
# Footer
# ======================================================
st.markdown("---")
st.caption(
    "Catatan: Sistem ini merupakan prototipe DSS berbasis agentic control "
    "dan tidak menggantikan kewenangan pengambil kebijakan."
)