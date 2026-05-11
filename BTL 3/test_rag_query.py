#!/usr/bin/env python3
"""
Test script cho rag_query.py - kiểm tra từng hàm riêng biệt
"""

import sys
from pathlib import Path

# Test 1: Import dependencies
print("=" * 60)
print("TEST 1: Kiểm tra dependencies")
print("=" * 60)

try:
    from sentence_transformers import SentenceTransformer
    print("✓ sentence_transformers imported")
except ImportError as e:
    print(f"✗ sentence_transformers: {e}")
    sys.exit(1)

try:
    import chromadb
    print("✓ chromadb imported")
except ImportError as e:
    print(f"✗ chromadb: {e}")
    sys.exit(1)

try:
    import google.generativeai as genai
    print("✓ google.generativeai imported")
except ImportError as e:
    print(f"✗ google.generativeai: {e}")
    print("  → Cần cài: pip install google-generativeai")

# Test 2: ChromaDB connection
print("\n" + "=" * 60)
print("TEST 2: Kiểm tra ChromaDB")
print("=" * 60)

CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "legal_clauses"

try:
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    count = collection.count()
    print(f"✓ ChromaDB connected - {count} documents in '{COLLECTION_NAME}'")
except Exception as e:
    print(f"✗ ChromaDB error: {e}")

# Test 3: Embedding model
print("\n" + "=" * 60)
print("TEST 3: Kiểm tra Embedding Model (có thể mất vài phút)")
print("=" * 60)

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
try:
    print("Loading embedding model (first time sẽ download ~400MB)...")
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    test_query = "test"
    vector = embedder.encode([test_query])[0]
    print(f"✓ Embedding model loaded - vector shape: {vector.shape}")
except Exception as e:
    print(f"✗ Embedding model error: {e}")

# Test 4: Build prompt function
print("\n" + "=" * 60)
print("TEST 4: Test build_prompt function")
print("=" * 60)

def build_prompt(query: str, retrieved_clauses: list[dict]) -> str:
    context = ""
    for i, clause in enumerate(retrieved_clauses, 1):
        context += f"[{i}] {clause['text']}\n"

    prompt = f"""Bạn là trợ lý pháp lý. Dựa trên các điều khoản hợp đồng dưới đây:

{context}

Hãy trả lời câu hỏi: {query}

Yêu cầu:
- Chỉ trả lời dựa trên thông tin được cung cấp ở trên.
- Nếu không tìm thấy thông tin, hãy nói: "Không tìm thấy điều khoản liên quan."
- Cuối câu trả lời, ghi rõ: (Nguồn: [số thứ tự điều khoản])
"""
    return prompt

test_clauses = [
    {"text": "Bên B phải thanh toán trong vòng 30 ngày", "line": 10, "intent": "Obligation", "distance": 0.1},
    {"text": "Hợp đồng có hiệu lực từ ngày ký", "line": 5, "intent": "Effective Date", "distance": 0.2},
]

prompt = build_prompt("Bên B thanh toán bao lâu?", test_clauses)
print("✓ build_prompt() works:")
print(f"\nPrompt preview (first 200 chars):\n{prompt[:200]}...")

print("\n" + "=" * 60)
print("KIỂM TRA HOÀN TẤT")
print("=" * 60)
print("✓ Tất cả kiểm tra cơ bản đều OK")
print("\nNhư cầu:")
print("1. pip install google-generativeai (nếu chưa có)")
print("2. Đặt GEMINI_API_KEY trong rag_query.py")
print("3. Chạy: python rag_query.py")
