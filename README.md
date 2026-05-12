# NLP Legal Contract Analysis Project

Dự án phân tích văn bản pháp luật và hợp đồng sử dụng các kỹ thuật xử lý ngôn ngữ tự nhiên (NLP). Hệ thống bao gồm từ bước tiền xử lý, trích xuất thực thể (NER), gán nhãn vai trò ngữ nghĩa (SRL) đến xây dựng hệ thống hỏi đáp thông minh (RAG).

## 📂 Cấu trúc thư mục

Dự án được tổ chức thành các Module bài tập lớn (BTL) theo trình tự xử lý:

*   **BTL 1: Tiền xử lý & Trích xuất mệnh đề**
    *   `extract.py`: Trích xuất và làm sạch dữ liệu từ CSV/Text, tách văn bản thành các mệnh đề độc lập.
*   **BTL 2: Phân tích chuyên sâu (NER & SRL)**
    *   `train_ner.py`: Huấn luyện mô hình spaCy để nhận diện các thực thể pháp luật (LAW, PARTY, DATE, MONEY...).
    *   `srl.py`: Gán nhãn vai trò ngữ nghĩa (Agent, Predicate, Theme...) cho các mệnh đề.
    *   `labeled_NER.jsonl`: Dữ liệu gán nhãn chuẩn cho NER.
*   **BTL 3: Hệ thống RAG (Retrieval-Augmented Generation)**
    *   `rag_build_db.py`: Xây dựng cơ sở dữ liệu vector bằng ChromaDB từ các mệnh đề đã xử lý.
    *   `rag_query.py`: Xử lý truy vấn và kết nối với Gemini LLM để sinh câu trả lời.
    *   `app.py`: Giao diện Chatbot người dùng (Streamlit).
*   **output/**: Chứa các kết quả trung gian (`clauses.txt`, `srl_results.json`, `ner_results.json`...).

## 🛠 Yêu cầu hệ thống

*   Python 3.10+
*   Virtual Environment (Khuyến nghị)

### Cài đặt thư viện:
```bash
pip install pandas underthesea spacy chromadb sentence-transformers google-generativeai streamlit tf-keras
python -m spacy download vi_core_news_lg
```

## 🚀 Hướng dẫn thực hiện (Pipeline)

Để hệ thống hoạt động chính xác, hãy chạy theo thứ tự sau:

### Bước 1: Trích xuất mệnh đề (BTL 1)
```bash
python "BTL 1/extract.py"
```
*Kết quả:* Tạo ra `output/clauses.txt`.

### Bước 2: Phân tích thực thể và ngữ nghĩa (BTL 2)
```bash
# Huấn luyện mô hình NER (nếu cần)
python "BTL 2/train_ner.py"

# Gán nhãn vai trò ngữ nghĩa (SRL)
python "BTL 2/srl.py"
```
*Kết quả:* Tạo ra `output/srl_results.json`.

### Bước 3: Xây dựng Database & Chạy Chatbot (BTL 3)
1. **Xây dựng Vector DB:**
   ```bash
   python "BTL 3/rag_build_db.py"
   ```
2. **Cấu hình Gemini API:** 
   Mở file `BTL 3/rag_query.py` và điền `API_KEY` của bạn vào biến `GEMINI_API_KEY`.
3. **Khởi chạy Giao diện:**
   ```bash
   streamlit run "BTL 3/app.py"
   ```

## ⚙️ Công nghệ sử dụng

*   **Tách câu & từ:** [Underthesea](https://github.com/underthesea/underthesea).
*   **NER:** [spaCy](https://spacy.io/) với kiến trúc transformer.
*   **Embedding:** `paraphrase-multilingual-MiniLM-L12-v2`.
*   **Vector Database:** [ChromaDB](https://www.trychroma.com/).
*   **LLM:** [Google Gemini API](https://aistudio.google.com/).
*   **UI:** [Streamlit](https://streamlit.io/).

---
*Ghi chú: Nếu gặp lỗi hiển thị tiếng Việt trên Terminal Windows, hãy chạy lệnh `$env:PYTHONIOENCODING="utf-8"` trước khi thực thi script.*
