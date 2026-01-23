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
# Inisialisasi Session State (WAJIB)
# ======================================================
if "destinasi_input" not in st.session_state:
    st.session_state["destinasi_input"] = "Danau Toba"


# ======================================================
# OpenRouter Config 
# ======================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    st.error("OPENROUTER_API_KEY belum diset di Streamlit Secrets.")
    st.stop()

# ======================================================
# Destinasi Valid (KUNCI SISTEM)
# ======================================================
DESTINASI_VALID = ["Danau Toba", "Candi Borobudur"]

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
# Load Dataset
# ======================================================
DATA_PATH = "db_listra.jsonl"

if not os.path.exists(DATA_PATH):
    st.error("Dataset db_listra.jsonl tidak ditemukan.")
    st.stop()

dataset_sample = load_jsonl(DATA_PATH, limit=3)
context_data = build_context_from_input(dataset_sample)

# ======================================================
# UI
# ======================================================
st.title("🌿 Agentic Decision Support System (DSS) Ekowisata")
st.markdown(
    "Prototipe sistem pendukung keputusan berbasis **storytelling multimodal** "
    "untuk mendukung kebijakan ekowisata berkelanjutan."
)

with st.expander("🔍 Contoh Data Ulasan Wisatawan (JSONL)"):
    st.json(dataset_sample)

st.subheader("📥 Konteks Pengambilan Keputusan Kebijakan")

# INPUT ASLI PROF (TIDAK DIUBAH)
#destinasi = st.text_input("Nama Destinasi Wisata", "Danau Toba")
destinasi = st.text_input(
    "Nama Destinasi Wisata",
    value="Danau Toba",
    key="destinasi_input"
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
# VALIDASI DATA (ANTI HALUSINASI)
# ======================================================
if not context_data.strip():
    st.warning("Data ulasan kosong. Pastikan file JSONL berisi field 'input'.")
    st.stop()

# ======================================================
# VALIDASI DESTINASI (KUNCI DOMAIN)
# ======================================================
if destinasi not in DESTINASI_VALID:
    st.error(
        "🙏 Maaf, destinasi yang Anda masukkan tidak tersedia.\n\n"
        "Sistem ini hanya mendukung **Danau Toba** dan **Candi Borobudur** "
        "sesuai dengan cakupan data penelitian."
    )
    # RESET KE MENU AWAL (AUTO)
    st.session_state["destinasi_input"] = "Danau Toba"
    st.stop()

# ======================================================
# DSS Inference
# ======================================================
if st.button("🧠 Generate Storytelling & Rekomendasi Kebijakan"):
    with st.spinner("Melakukan penalaran kebijakan berbasis storytelling..."):

        prompt = (
            f"Anda adalah sistem pendukung keputusan kebijakan ekowisata berkelanjutan.\n\n"
            f"ATURAN WAJIB:\n"
            f"1. Fokus HANYA pada destinasi: {destinasi}\n"
            f"2. DILARANG menyebut destinasi wisata lain.\n"
            f"3. Analisis HARUS berbasis data ulasan di bawah ini.\n\n"
            f"DATA ULASAN WISATAWAN:\n{context_data}\n\n"
            f"TUJUAN KEBIJAKAN:\n{tujuan_kebijakan}\n\n"
            f"TUGAS:\n"
            f"1. Susun storytelling kebijakan khusus untuk {destinasi}.\n"
            f"2. Identifikasi isu utama dari pengalaman pengunjung.\n"
            f"3. Berikan 3 rekomendasi kebijakan konkret.\n\n"
            f"Gunakan bahasa formal kebijakan dan berbasis bukti."
        )

        payload = {
            "model": "meta-llama/llama-3.2-3b-instruct",
            "messages": [
                {"role": "system", "content": "Anda hanya membahas Danau Toba atau Candi Borobudur."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
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

# ======================================================
# Footer
# ======================================================
st.markdown("---")
st.caption(
    "Catatan: Sistem ini merupakan prototipe DSS berbasis agentic control "
    "dan tidak menggantikan kewenangan pengambil kebijakan."
)
