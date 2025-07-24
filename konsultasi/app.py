import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN MODEL
# ==============================================================================

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah chatbot asisten kesehatan wanita yang profesional, ramah, dan menjaga kerahasiaan. Tugasmu adalah membantu pengguna perempuan memahami kondisi kesehatannya, memberikan saran awal yang aman, dan mengarahkan ke dokter jika diperlukan. Jangan pernah memberikan diagnosis pasti atau resep obat tanpa konfirmasi dokter."]
    },
    {
        "role": "model",
        "parts": ["Baik! Saya siap membantu Anda. Silakan sampaikan keluhan yang Anda rasakan."]
    }
]

# ==============================================================================
# FUNGSI UTAMA CHATBOT UNTUK STREAMLIT
# ==============================================================================

st.set_page_config(page_title="Asisten Kesehatan Wanita AI")
st.title("????? Asisten Kesehatan Wanita AI")
st.write("Profesional, ramah, dan menjaga kerahasiaan. Saya siap membantu Anda memahami kondisi kesehatan, memberikan saran awal yang aman, dan mengarahkan ke dokter jika diperlukan.")

# Mengambil API Key dari Streamlit Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Kesalahan konfigurasi API Key: {e}")
    st.warning("Pastikan Anda telah menambahkan GEMINI_API_KEY di Streamlit Secrets.")
    st.stop() # Hentikan eksekusi jika API Key tidak ada

# Inisialisasi model
try:
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )
except Exception as e:
    st.error(f"Kesalahan saat inisialisasi model '{MODEL_NAME}': {e}")
    st.stop()

# Inisialisasi riwayat chat di Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = INITIAL_CHATBOT_CONTEXT

# Menampilkan riwayat chat
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["parts"][0])
    elif message["role"] == "model":
        with st.chat_message("assistant"):
            st.markdown(message["parts"][0])

# Input pengguna
user_query = st.chat_input("Tulis pesan Anda di sini...")

if user_query:
    # Tambahkan pesan pengguna ke riwayat
    st.session_state.chat_history.append({"role": "user", "parts": [user_query]})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Kirim pesan ke model dan dapatkan respons
    try:
        chat_session = model.start_chat(history=st.session_state.chat_history)
        with st.chat_message("assistant"):
            with st.spinner("Sedang memproses..."):
                response = chat_session.send_message(user_query, request_options={"timeout": 60})
                if response and response.text:
                    st.markdown(response.text)
                    st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
                else:
                    st.error("Maaf, saya tidak bisa memberikan balasan. Respons API kosong atau tidak valid.")
                    # Hapus pesan terakhir jika respons tidak valid agar tidak tersimpan di riwayat
                    st.session_state.chat_history.pop()

    except Exception as e:
        st.error(f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}")
        st.warning("Pastikan API Key Anda benar dan koneksi internet stabil.")
        # Hapus pesan terakhir jika terjadi error agar tidak tersimpan di riwayat
        st.session_state.chat_history.pop()

# Tombol reset chat (opsional)
if st.button("Mulai Percakapan Baru"):
    st.session_state.chat_history = INITIAL_CHATBOT_CONTEXT
    st.experimental_rerun()