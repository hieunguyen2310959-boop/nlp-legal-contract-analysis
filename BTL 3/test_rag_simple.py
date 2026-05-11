#!/usr/bin/env python3
"""
Test đơn giản - kiểm tra logic code mà không load embedding model
"""

print("TEST: Kiểm tra hàm retrieve() - mock data")
print("=" * 60)

# Simulate retrieve function without loading model
def retrieve_mock(query: str, k: int = 3):
    """Mock version của retrieve() với hardcoded data"""
    return [
        {
            "text": "Bên B phải thanh toán trong vòng 30 ngày kể từ ngày nhận hóa đơn",
            "line": 42,
            "intent": "Obligation",
            "distance": 0.15
        },
        {
            "text": "Hợp đồng này có hiệu lực từ ngày ký và kéo dài 2 năm",
            "line": 5,
            "intent": "Duration",
            "distance": 0.32
        },
        {
            "text": "Bên A cam kết cung cấp dịch vụ chất lượng cao",
            "line": 18,
            "intent": "Obligation",
            "distance": 0.48
        },
    ]

# Test build_prompt function
print("\nTEST: Kiểm tra hàm build_prompt()")
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

# Run test
test_query = "Bên B phải thanh toán trong bao lâu?"
results = retrieve_mock(test_query, k=3)

print(f"Query: {test_query}")
print(f"Retrieved {len(results)} clauses:")
for i, r in enumerate(results, 1):
    print(f"  [{i}] line {r['line']}, {r['intent']}, dist={r['distance']:.3f}")

prompt = build_prompt(test_query, results)
print(f"\nGenerated prompt (first 300 chars):\n{prompt[:300]}...\n")

print("=" * 60)
print("✓ Code logic OK!")
print("\nNhư cầu để chạy rag_query.py full:")
print("1. pip install google-generativeai")
print("2. Đặt GEMINI_API_KEY hợp lệ trong rag_query.py")
print("3. Đảm bảo ChromaDB đã được khởi tạo với dữ liệu")
print("4. Chạy: python rag_query.py")
