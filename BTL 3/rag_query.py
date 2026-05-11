"""
BTL 3.3 — Bước 2: Retrieval + Generation
==========================================
Các hàm cốt lõi của hệ thống RAG:
    - retrieve(): tìm k mệnh đề liên quan nhất từ ChromaDB
    - generate(): gọi LLM sinh câu trả lời dựa trên context

File này được import bởi app.py.
"""

from pathlib import Path


# ── Cấu hình ─────────────────────────────────────────────────────────────────

CHROMA_DB_PATH  = "./chroma_db"
COLLECTION_NAME = "legal_clauses"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
GEMINI_API_KEY  = "Enterthekeyhere:)"
TOP_K = 3


# ── Khởi tạo (lazy — chỉ load khi cần) ─────────────────────────────────────

_embedder = None
_client = None
_collection = None
model = None

def _init_rag_system():
    """Khởi tạo embedding model, ChromaDB, và LLM (chỉ chạy 1 lần)."""
    global _embedder, _client, _collection, model

    if _embedder is not None:
        return

    from sentence_transformers import SentenceTransformer
    import chromadb

    db_path = Path(CHROMA_DB_PATH)
    if not db_path.exists():
        raise FileNotFoundError(f"ChromaDB folder không tìm thấy: {CHROMA_DB_PATH}")

    _embedder = SentenceTransformer(EMBEDDING_MODEL)
    _client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    _collection = _client.get_collection(COLLECTION_NAME)

    import google.generativeai as genai  # type: ignore
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
# ── Hàm Retrieval ─────────────────────────────────────────────────────────────

def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """
    Tìm k mệnh đề liên quan nhất với câu hỏi.

    Returns:
        list[dict]: mỗi phần tử có dạng
            {"text", "line", "intent", "distance"}
    """
    _init_rag_system()
    vector = _embedder.encode([query])[0]
    results = _collection.query(
        query_embeddings=[vector.tolist()],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    return [
        {
            "text":     doc,
            "line":     meta.get("line", i),
            "intent":   meta.get("intent", "Unknown"),
            "distance": dis,
        }
        for i, (doc, meta, dis) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ))
    ]



# ── Hàm Generation ────────────────────────────────────────────────────────────

def build_prompt(query: str, retrieved_clauses: list[dict]) -> str:
    """Tạo prompt gửi cho LLM từ câu hỏi và các mệnh đề context."""
    context = "\n".join(
        f"[{i}] {clause['text']}"
        for i, clause in enumerate(retrieved_clauses, 1)
    )
    return f"""Bạn là trợ lý pháp lý. Dựa trên các điều khoản hợp đồng dưới đây:

{context}

Hãy trả lời câu hỏi: {query}

Yêu cầu:
- Chỉ trả lời dựa trên thông tin được cung cấp ở trên.
- Nếu không tìm thấy thông tin, hãy nói: "Không tìm thấy điều khoản liên quan."
- Cuối câu trả lời, ghi rõ: (Nguồn: [số thứ tự điều khoản])
"""

def generate(query: str, retrieved_clauses: list[dict]) -> str:
    """Gọi LLM để sinh câu trả lời từ query và context đã retrieve."""
    _init_rag_system()
    prompt = build_prompt(query, retrieved_clauses)

    try:
        response = model.generate_content(prompt)
    except Exception as exc:
        message = str(exc).lower()
        is_quota_error = "resourceexhausted" in exc.__class__.__name__.lower() or "quota" in message or "429" in message
        if is_quota_error:
            source_lines = ", ".join(str(clause.get("line", "?")) for clause in retrieved_clauses)
            return (
                "Không thể sinh câu trả lời lúc này vì đã vượt quota Gemini API. "
                f"Các điều khoản liên quan đã được truy xuất ở các dòng: {source_lines}."
            )
        raise

    return getattr(response, "text", "").strip() or "Không nhận được nội dung trả lời từ Gemini."


# ── Test nhanh ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_query = "Bên B phải thanh toán trong bao lâu?"
    print(f"Query: {test_query}\n")

    results = retrieve(test_query, k=3)
    print("=== Top 3 mệnh đề liên quan ===")
    for i, r in enumerate(results, 1):
        print(f"[{i}] (line {r['line']}, {r['intent']}, dist={r['distance']:.3f})")
        print(f"     {r['text'][:100]}")

    print("\n=== Câu trả lời từ LLM ===")
    answer = generate(test_query, results)
    print(answer)
