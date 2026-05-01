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
    Điểm ngắt: dấu chấm phẩy, liên từ 'và', 'hoặc', 'nếu', 'nhưng'...
    """
    separators = r'(;|,\s*và\b|,\s*hoặc\b|\bnếu\b|\bnhưng\b|\bđồng thời\b|\btrong khi\b)'
    parts = re.split(separators, sentence)

    final_clauses = []
    temp_clause = ""
    for part in parts:
        if re.match(separators, part.strip()):
            temp_clause += part
        else:
            if temp_clause:
                final_clauses.append(temp_clause.strip())
            temp_clause = part

    if temp_clause:
        final_clauses.append(temp_clause.strip())

    return [c for c in final_clauses if len(c) > 10]

# 1. Đọc file CSV đã tải về local
df = pd.read_csv("vietnam_legal_documents_train_local.csv")

# 2. Parse và làm sạch cột 'context', lấy 100 dòng đầu
raw_texts = []
for raw in df['context'].head(100):
    text = parse_context(raw)
    text = preprocess_legal_text(text)
    if text:
        raw_texts.append(text)

# 3. Lưu vào input/raw_contracts.txt
with open("input/raw_contracts.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(raw_texts))

# 4. Tách mệnh đề và lưu vào output/clauses.txt
all_clauses = []
for text in raw_texts:
    # Bước A: Tách câu cơ bản bằng underthesea
    sentences = sent_tokenize(text)
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 10:
            continue
        # Bước B: Tách mệnh đề độc lập (Task 1.1)
        clauses = split_into_clauses(sent)
        all_clauses.extend(clauses)

with open("output/clauses.txt", "w", encoding="utf-8") as f:
    for clause in all_clauses:
        f.write(f"{clause.strip()}\n")

print(f"Hoàn thành trích xuất từ cột 'context'!")
print(f"- File thô: input/raw_contracts.txt")
print(f"- File mệnh đề: output/clauses.txt ({len(all_clauses)} dòng)")