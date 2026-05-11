"""
BTL 3.3 — Bước 3: Giao diện Streamlit
=======================================
Cách chạy:
    streamlit run app.py

Yêu cầu: đã chạy rag_build_db.py trước để có thư mục chroma_db/
"""

import streamlit as st
from rag_query import retrieve, generate


# ── Cấu hình giao diện ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Contract QA Chatbot",
    page_icon="⚖️",
    layout="centered",
)

st.title("⚖️ Hỏi đáp Hợp đồng")
st.caption("Hệ thống trả lời câu hỏi về hợp đồng dựa trên RAG")

# Khởi tạo session state
if "initialized" not in st.session_state:
    st.session_state.initialized = False


# ── Cache model/DB để không load lại mỗi lần query ───────────────────────────

@st.cache_resource(show_spinner="Đang tải model và cơ sở dữ liệu...")
def load_rag_system():
    """Khởi tạo embedding model + ChromaDB một lần duy nhất."""
    from sentence_transformers import SentenceTransformer
    import chromadb
    import google.generativeai as genai  # type: ignore
    from rag_query import CHROMA_DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL, GEMINI_API_KEY

    embedder = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    genai.configure(api_key=GEMINI_API_KEY)
    llm = genai.GenerativeModel("gemini-2.5-flash")
    return embedder, collection, llm

load_rag_system()  # trigger load sớm khi app khởi động


# ── Phần nhập câu hỏi ────────────────────────────────────────────────────────

query = st.text_input(
    label="Nhập câu hỏi của bạn:",
    placeholder="Ví dụ: Bên B phải thanh toán trong bao lâu?",
)

col1, col2 = st.columns([1, 4])
with col1:
    submit = st.button("Tìm kiếm", type="primary")
with col2:
    show_sources = st.checkbox("Hiển thị mệnh đề nguồn", value=True)


# ── Xử lý khi user nhấn nút ──────────────────────────────────────────────────

if submit and query.strip():
    try:
        with st.spinner("Đang tìm kiếm..."):
            # Bước 1: Retrieval
            retrieved = retrieve(query, k=3)

            # Bước 2: Generation
            answer = generate(query, retrieved)

        # Hiển thị câu trả lời
        st.subheader("Câu trả lời")
        if answer:
            st.write(answer)
        else:
            st.warning("Chưa có câu trả lời.")

        # Hiển thị mệnh đề nguồn
        if show_sources and retrieved:
            st.subheader("Mệnh đề liên quan")
            for i, clause in enumerate(retrieved, 1):
                with st.expander(f"[{i}] Dòng {clause.get('line', '?')} — {clause.get('intent', '')}"):
                    st.write(clause.get("text", ""))
                    if clause.get("distance"):
                        st.caption(f"Độ liên quan: {1 - clause['distance']:.1%}")
    
    except Exception as e:
        st.error(f"Lỗi: {str(e)}")
        import traceback
        with st.expander("Chi tiết lỗi"):
            st.code(traceback.format_exc())

elif submit and not query.strip():
    st.error("Vui lòng nhập câu hỏi trước khi tìm kiếm.")


# ── Sidebar: thông tin hệ thống ───────────────────────────────────────────────

with st.sidebar:
    st.header("Thông tin hệ thống")
    st.markdown("""
    **Pipeline:**
    1. Embed câu hỏi → vector
    2. Tìm k=3 mệnh đề gần nhất (ChromaDB)
    3. Gửi context + câu hỏi → LLM
    4. Hiển thị câu trả lời + nguồn

    **Dữ liệu:**
    - `output/clauses.txt` — 721 mệnh đề
    - `output/intent_classification.txt`
    - `output/srl_results.json`

    **Model:**
    - Embedding: `paraphrase-multilingual-MiniLM-L12-v2`
    - LLM: Gemini 2.5 Flash
    """)
