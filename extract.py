import pandas as pd
from underthesea import sent_tokenize
import re
import os
import ast

# Tạo thư mục theo yêu cầu đặc tả
os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

def parse_context(raw):
    """Cột context chứa chuỗi dạng Python list -> parse ra text thuần."""
    if pd.isna(raw):
        return ""
    raw = str(raw).strip()
    try:
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, list):
            return " ".join(str(item) for item in parsed)
        return str(parsed)
    except Exception:
        return raw

def preprocess_legal_text(text):
    """Làm sạch text: bỏ ký tự xuống dòng, khoảng trắng thừa."""
    # Thay \n bằng dấu cách, loại khoảng trắng thừa
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Bỏ dấu ngoặc kép đầu/cuối nếu có
    text = text.strip('"\'')
    return text

def split_into_clauses(sentence):
    """Tách mệnh đề dựa trên ranh giới ngữ nghĩa (Tác vụ 1.1).

    Quy tắc tách:
      - Chỉ tách tại dấu chấm phẩy (;).
      - KHÔNG tách tại liên từ (và, hoặc, nếu, nhưng...) vì chúng
        thường nối các thành phần ngữ pháp bên trong cùng một mệnh đề,
        việc cắt ở đây sẽ phá vỡ ngữ nghĩa câu.
      - KHÔNG tách khi dấu ; nằm bên trong ngoặc đơn (...) vì đó là
        phần liệt kê phụ thuộc (ví dụ: "gồm: A; B; C").
    """
    # Duyệt từng ký tự để tách an toàn theo dấu ;
    # nhưng bỏ qua ; nằm trong ngoặc đơn.
    clauses = []
    current = []
    paren_depth = 0

    for ch in sentence:
        if ch == '(':
            paren_depth += 1
        elif ch == ')':
            paren_depth = max(0, paren_depth - 1)

        if ch == ';' and paren_depth == 0:
            # Gặp ; ngoài ngoặc -> kết thúc mệnh đề hiện tại
            current.append(ch)           # giữ lại dấu ; ở cuối mệnh đề
            clauses.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)

    # Phần còn lại sau dấu ; cuối cùng
    if current:
        clauses.append(''.join(current).strip())

    return [c for c in clauses if len(c) > 10]

# 1. Đọc dữ liệu đầu vào
CSV_PATH = "vietnam_legal_documents_train_local.csv"
RAW_PATH = "input/raw_contracts.txt"

raw_texts = []
if os.path.exists(CSV_PATH):
    # Đọc từ file CSV gốc (nếu còn)
    df = pd.read_csv(CSV_PATH)
    for raw in df['context'].head(100):
        text = parse_context(raw)
        text = preprocess_legal_text(text)
        if text:
            raw_texts.append(text)
elif os.path.exists(RAW_PATH):
    # Đọc từ file raw_contracts.txt đã được tạo trước đó
    # (Các đoạn văn cách nhau bởi dòng trống)
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    paragraphs = content.split("\n\n")
    for para in paragraphs:
        text = preprocess_legal_text(para)
        if text:
            raw_texts.append(text)
else:
    print("Lỗi: Không tìm thấy file CSV hoặc raw_contracts.txt!")
    exit(1)

# 3. Lưu vào input/raw_contracts.txt
with open("input/raw_contracts.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(raw_texts))

# Regex nhận diện câu bắt đầu bằng bullet / sub-item
# Ví dụ: a) ..., b) ..., đ) ..., - ..., 2.5. ..., 8.2.1 ...
_BULLET_RE = re.compile(
    r'^('
    r'[abcdeđghikl]\)\s'     # a) b) c) d) đ) e) g) h) i) k) l)
    r'|[abcdeđghikl]\.\s'    # a. b. c. ...
    r'|-\s'                  # - item
    r'|\d+\.\d+'             # 2.5  hoặc 8.2.1
    r')'
)

def merge_bullet_sentences(sentences):
    """Gộp các câu bắt đầu bằng bullet/sub-item trở lại câu cha.

    Sau khi sent_tokenize tách tại mỗi dấu chấm, các bullet item
    như "b) Chi trả lãi tiền vay." bị tách thành câu riêng.
    Hàm này ghép chúng lại với câu phía trước để giữ ngữ cảnh.
    """
    if not sentences:
        return sentences

    merged = [sentences[0].strip()]
    for sent in sentences[1:]:
        stripped = sent.strip()
        if not stripped:
            continue
        if _BULLET_RE.match(stripped):
            # Đây là bullet item → ghép vào câu trước
            merged[-1] = merged[-1] + " " + stripped
        else:
            merged.append(stripped)
    return merged

# 4. Tách mệnh đề và lưu vào output/clauses.txt
all_clauses = []
for text in raw_texts:
    # Bước A: Tách câu cơ bản bằng underthesea
    sentences = sent_tokenize(text)
    # Bước B: Gộp lại các bullet items bị tách rời
    sentences = merge_bullet_sentences(sentences)
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 10:
            continue
        # Bước C: Tách mệnh đề theo dấu ; (ngoài ngoặc)
        clauses = split_into_clauses(sent)
        all_clauses.extend(clauses)

with open("output/clauses.txt", "w", encoding="utf-8") as f:
    for clause in all_clauses:
        f.write(f"{clause.strip()}\n")

print(f"Done! Extracted from raw_contracts.txt")
print(f"- Raw file: input/raw_contracts.txt")
print(f"- Clauses file: output/clauses.txt ({len(all_clauses)} lines)")