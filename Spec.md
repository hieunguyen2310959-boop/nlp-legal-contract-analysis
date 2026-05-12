```
ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH
TRƯỜNG ĐẠI HỌC BÁCH KHOA
KHOA KHOA HỌC VÀ KỸ THUẬT MÁY TÍNH
```
```
ĐẶC TẢ BÀI TẬP LỚN
HỌC KỲ 252 NĂM HỌC 2025-
```
**TRÍCH XUẤT THÔNG TIN VÀ PHÂN TÍCH**

**NGỮ NGHĨA HỢP ĐỒNG PHÁP LÝ**

```
NGÀNH: KHOA HỌC MÁY TÍNH
MÔN: Xử lý Ngôn ngữ Tự nhiên
HÌNH THỨC: Bài tập nhóm (2–3 sinh viên)
——o0o——
Sản phẩm: Source Code + Báo cáo
Hình thức nộp: Báo cáo (PDF) & Git Repository Link
```
Thành phố Hồ Chí Minh, Tháng 2/


## Mục lục


- 1 Tiền xử lý và Phân tích cú pháp
   - 1.1 Tách mệnh đề
      - 1.1.1 Bài toán & Mục tiêu
      - 1.1.2 Input & Output
      - 1.1.3 Ví dụ
   - 1.2 Phân cụm danh từ
      - 1.2.1 Bài toán & Mục tiêu
      - 1.2.2 Input & Output
      - 1.2.3 Ví dụ
   - 1.3 Phân tích phụ thuộc
      - 1.3.1 Bài toán & Mục tiêu
      - 1.3.2 Input & Output
      - 1.3.3 Ví dụ
- 2 Trích xuất thông tin và Phân tích ngữ nghĩa
   - 2.1 Nhận dạng thực thể có tên tùy chỉnh (NER)
      - 2.1.1 Bài toán & Mục tiêu
      - 2.1.2 Input & Output
      - 2.1.3 Ví dụ
   - 2.2 Gắn nhãn vai trò ngữ nghĩa (SRL)
      - 2.2.1 Bài toán & Mục tiêu
      - 2.2.2 Input & Output
      - 2.2.3 Ví dụ
   - 2.3 Phân loại ý định
      - 2.3.1 Bài toán & Mục tiêu
      - 2.3.2 Input & Output
      - 2.3.3 Ví dụ
- 3 Ứng dụng trả lời câu hỏi về Hợp đồng
   - 3.1 Bài toán & Mục tiêu
   - 3.2 Lựa chọn 1: Hệ thống truy vấn dựa trên Luật
      - 3.2.1 Mục tiêu
      - 3.2.2 Ví dụ
      - 3.2.3 Yêu cầu
      - tion - RAG) 3.3 Lựa chọn 2: Chatbot kết hợp Truy xuất (Retrieval-Augmented Genera-
      - 3.3.1 Mục tiêu
      - 3.3.2 Ví dụ
      - 3.3.3 Yêu cầu


## Assignment 1

# Tiền xử lý và Phân tích cú pháp

_Bài tập này tập trung vào việc xây dựng các thành phần cơ bản để xử lý tài liệu hợp đồng
pháp lý. Sinh viên được yêu cầu triển khai các mô-đun Xử lý Ngôn ngữ Tự nhiên cốt lõi
nhằm chuyển đổi văn bản hợp đồng không cấu trúc thành các biểu diễn có cấu trúc về
mặt cú pháp._

### 1.1 Tách mệnh đề

#### 1.1.1 Bài toán & Mục tiêu

Các hợp đồng pháp lý thường chứa những câu dài và phức tạp với nhiều mệnh đề phụ,
điều kiện và các phép liệt kê. Những câu như vậy rất khó để xử lý trực tiếp cho các tác
vụ trích xuất thông tin phức tạp hơn.
Mục tiêu của tác vụ này là phát triển một thuật toán phân tách một câu phức thành các
mệnh đề độc lập về mặt ngữ nghĩa. Mỗi mệnh đề kết quả phải thể hiện một đơn vị có ý
nghĩa, có thể được phân tích riêng biệt.

#### 1.1.2 Input & Output

**Input:**

- File:input/raw_contracts.txt
- Nội dung: Chứa văn bản hợp đồng thô do sinh viên chọn.


**Output:**

- File:output/clauses.txt
- Nội dung: Mỗi dòng chứa đúng một mệnh đề độc lập.

#### 1.1.3 Ví dụ

**Input:**

Bên B sẽ thanh toán toàn bộ tiền thuê trước ngày 5 hàng tháng, và
,→ nếu thanh toán trễ hạn, mức phạt 1% mỗi ngày sẽ được áp dụng.

**Output:**

Bên B sẽ thanh toán toàn bộ tiền thuê trước ngày 5 hàng tháng.
Nếu thanh toán trễ hạn, mức phạt 1% mỗi ngày sẽ được áp dụng.

**Giải thích:** Câu gốc chứa một mệnh đề chính và một mệnh đề điều kiện.
Thuật toán phải tách biệt chúng một cách chính xác trong khi vẫn giữ nguyên tính toàn
vẹn về mặt ngữ nghĩa.

### 1.2 Phân cụm danh từ

#### 1.2.1 Bài toán & Mục tiêu

Trong các tài liệu pháp lý, các cụm danh từ thường đại diện cho các thực thể chính như
các bên ký kết, số tiền tài chính, thời hạn hoặc đối tượng hợp đồng. Việc xác định các
cụm danh từ này là cần thiết cho quá trình gán nhãn vai trò ngữ nghĩa và trích xuất thông
tin sau này.
Mục tiêu của tác vụ này là phát hiện và gắn nhãn các cụm danh từ trong mỗi mệnh đề
bằng cách sử dụng lược đồ gắn nhãn IOB.

#### 1.2.2 Input & Output

**Input:**


- File:output/clauses.txt
- Mỗi mệnh đề thu được từ Tác vụ 1.1 sẽ được xử lý độc lập.

**Output:**

- File:output/chunks.txt
- Mỗi token phải được gắn nhãn theo định dạng IOB.
    **-** B-NP: Bắt đầu cụm danh từ
    **-** I-NP: Bên trong cụm danh từ
    **-** O: Bên ngoài cụm danh từ

#### 1.2.3 Ví dụ

**Input:**

Bên B sẽ thanh toán toàn bộ tiền thuê

**Output (IOB format):**

Bên B-NP
B I-NP
sẽ O
thanh O
toán O
toàn B-NP
bộ I-NP
tiền I-NP
thuê I-NP

. O

**Giải thích:**
”Bên B” and ”toàn bộ tiền thuê” là các cụm danh từ, và lược đồ gắn nhãn xác định rõ
ràng ranh giới của từng cụm danh từ.


### 1.3 Phân tích phụ thuộc

#### 1.3.1 Bài toán & Mục tiêu

Hiểu được các mối quan hệ ngữ pháp giữa các từ trong một mệnh đề là rất quan trọng
để xác định các vai trò cú pháp như chủ ngữ, vị ngữ và tân ngữ. Mục tiêu của tác vụ này
là thực hiện phân tích cú pháp phụ thuộc trên mỗi mệnh đề để xác định các mối quan
hệ chủ-phụ và các vai trò cú pháp. Sinh viên có thể sử dụng một công cụ phân tích phụ
thuộc có sẵn mà không bắt buộc phải huấn luyện lại từ đầu.

#### 1.3.2 Input & Output

**Input:**

- File:output/clauses.txt
- Mỗi mệnh đề được phân tích cú pháp một cách độc lập.

**Output:**

- File:output/dependency.json(hoặc CoNLL-U format)
- Đối với mỗi token, đầu ra phải bao gồm:
    **-** Token
    **-** Head
    **-** Mối quan hệ phụ thuộc (e.g., root, nsubj, obj, advcl)

#### 1.3.3 Ví dụ

**Input clause:**

Bên B sẽ thanh toán toàn bộ tiền thuê.

**Output (đơn giản hoá):**


thanh toán -> root
Bên B -> nsubj (head: thanh toán)
khoản -> obj (head: thanh toán)

**Giải thích:**
Cây phụ thuộc xác định:

- Động từ chính (root)
- Chủ ngữ danh từ (nsubj)
- Tân ngữ (obj)

Cấu trúc cú pháp này hỗ trợ việc hiểu chính xác mệnh đề và cho phép thực hiện các tác
vụ trích xuất ngữ nghĩa sau này.


## Assignment 2

# Trích xuất thông tin và Phân tích

# ngữ nghĩa

_Bài tập này tập trung vào việc trích xuất các thông tin ngữ nghĩa có cấu trúc từ các mệnh
đề của hợp đồng pháp lý. Dựa trên các module xử lý cú pháp ở Bài tập 1, sinh viên cần
triển khai các kỹ thuật NLP nâng cao để nhận dạng các thực thể đặc thù của miền, xác
định vai trò ngữ nghĩa và phân loại ý định mệnh đề. Mục tiêu là chuyển đổi các mệnh
đề có cấu trúc thành các biểu diễn có ý nghĩa, nắm bắt được ”ai làm gì” và chức năng
pháp lý của từng mệnh đề._

### 2.1 Nhận dạng thực thể có tên tùy chỉnh (NER)

#### 2.1.1 Bài toán & Mục tiêu

Các hợp đồng pháp lý chứa các thực thể đặc thù mà các hệ thống NER thông thường
không bao quát hết, ví dụ như các bên ký kết, số tiền, thời hạn, các điều khoản phạt và
luật điều chỉnh. Mục tiêu là thiết kế và huấn luyện (hoặc tinh chỉnh) một mô hình NER
dành riêng cho lĩnh vực hợp đồng.
Lược đồ thực thể định nghĩa rõ ràng có thể bao gồm:

- PARTY (e.g., Bên A, Bên B, Người lao động)
- MONEY (e.g., 10,000,000 VNĐ)


- DATE (e.g., hạn nộp)
- RATE (e.g., lợi nhuận, mức chịu thuế)
- PENALTY
- LAW

#### 2.1.2 Input & Output

**Input:**

- Các mệnh đề từ Bài tập 1 (output/clauses.txt)
- Tập dữ liệu huấn luyện đã được gán nhãn do sinh viên tạo ra.

**Output:**

- File:output/ner_results.json
- Mỗi mệnh đề phải chứa các thực thể đã được xác định kèm theo ranh giới (spans)
    và nhãn của chúng.

#### 2.1.3 Ví dụ

**Input:**

Bên B phải thanh toán 10,000,000 VNĐ trước ngày 05/5/2024.

**Output (JSON format):**

{
"entities": [
{"text": "Bên B", "label": "PARTY"},
{"text": "10,000,000 VNĐ", "label": "MONEY"},
{"text": "ngày 05/5/2024", "label": "DATE"}
]
}


**Giải thích:**
Mô hình phải nhận dạng chính xác các thực thể đặc thù và phân loại chúng theo lược đồ
đã định nghĩa.

### 2.2 Gắn nhãn vai trò ngữ nghĩa (SRL)

#### 2.2.1 Bài toán & Mục tiêu

Mặc dù NER nhận dạng được các thực thể, nhưng nó không xác định vai trò ngữ nghĩa
(”ai làm gì với ai”) của chúng trong câu.
Mục tiêu là áp dụng một số mô hình để thực hiện SRL, gán vai trò ngữ nghĩa cho các
thực thể dựa trên vị ngữ chính.
Các vai trò thường thấy bao gồm:

- Agent
- Predicate
- Theme
- Recipient
- Time
- Condition

#### 2.2.2 Input & Output

**Input:**

- Các mệnh đề từ Bài tập 1
- Các thực thể có tên được phát hiện trong Tác vụ 2.1.

**Output:**

- File:output/srl_results.json
- Biểu diễn có cấu trúc của các vai trò ngữ nghĩa cho từng mệnh đề.


#### 2.2.3 Ví dụ

**Input clause:**

Bên A phải bàn giao vật tư cho bên B.

**Output (simplified):**

{
"predicate": "bàn giao",
"roles": {
"Agent": "Bên A",
"Theme": "vật tư",
"Recipient": "Bên B"
}
}

**Giải thích:**
Mô hình SRL phải xác định vị ngữ chính và gán các vai trò tương ứng.

### 2.3 Phân loại ý định

#### 2.3.1 Bài toán & Mục tiêu

Các mệnh đề pháp lý phải được phân loại theo ý định chức năng của chúng. Mục tiêu là
phân loại mỗi mệnh đề vào:

- Obligation
- Prohibition
- Right
- Termination Condition

Sinh viên có thể dùng mô hình cơ sở như TF-IDF kết hợp Logistic Regression và so sánh
với bộ phân loại dựa trên transformer.


#### 2.3.2 Input & Output

**Input:**

- Đầu vào là các mệnh đề từ Bài tập lớn 1

**Output:**

- File:output/intent_classification.txt
- Mỗi dòng chứa một mệnh đề và nhãn dự đoán tương ứng.

#### 2.3.3 Ví dụ

**Input:**

Bên B phải trả đầy đủ tiền thuê trước ngày 5 hàng tháng.

**Output:**

Obligation

**Giải thích:**
Mệnh đề thể hiện một nhiệm vụ bắt buộc nên được phân loại là Nghĩa vụ.


## Assignment 3

# Ứng dụng trả lời câu hỏi về Hợp

# đồng

Đây là bài tập tùy chọn, sinh viên hoàn thành sẽ được điểm thưởng cho các bài tập khác.
_Bài tập này tập trung vào việc xây dựng một hệ thống trả lời câu hỏi hợp đồng có tính
tương tác, dựa trên các đầu ra có cấu trúc được tạo ra ở Bài tập 1 và 2. Sinh viên được
yêu cầu chuyển đổi quy trình trích xuất thông tin của mình thành một ứng dụng có thể
sử dụng được, cho phép người dùng cuối truy vấn thông tin hợp đồng bằng ngôn ngữ tự
nhiên. Mục tiêu là tích hợp các biểu diễn cú pháp và ngữ nghĩa vào một hệ thống chức
năng và có thể minh họa được._

### 3.1 Bài toán & Mục tiêu

Sau khi trích xuất các thông tin có cấu trúc (các mệnh đề, các thực thể, các vai trò ngữ
nghĩa, và ý định của mệnh đề), bước tiếp theo là xây dựng một ứng dụng có khả năng trả
lời các câu hỏi về hợp đồng.
Hệ thống phải:

- Chấp nhận các truy vấn của người dùng bằng ngôn ngữ tự nhiên.
- Truy xuất các thông tin hợp đồng có liên quan.
- Tạo ra một câu trả lời rõ ràng và chính xác.


- Cung cấp khả năng truy xuất nguồn gốc về mệnh đề gốc.

Sinh viên phải triển khai một giao diện tương tác đơn giản, có thể là:

- Console app, hoặc
- Giao diện web (e.g., Flask, FastAPI, Streamlit, etc.).

Sinh viên phải chọn **một** trong các phương pháp triển khai sau đây.

### 3.2 Lựa chọn 1: Hệ thống truy vấn dựa trên Luật

#### 3.2.1 Mục tiêu

Sinh viên phải thiết kế một công cụ truy vấn hoạt động trên các file JSON được tạo ra ở
Bài tập 2.
Hệ thống nên ánh xạ các truy vấn của người dùng tới các biểu diễn có cấu trúc như:

- Agent
- Predicate
- Theme
- Time
- Intent

#### 3.2.2 Ví dụ

**Input:**

Khi nào Bên B bị phạt?

**Logic:**

- Xác định Agent = Bên B
- Xác định Intent = bị phạt


- Truy xuất mệnh đề tương ứng

**Output:**

Bên B sẽ bị phạt nếu việc thanh toán bị chậm trễ quá 5 ngày.
(Source: ...)

#### 3.2.3 Yêu cầu

- Logic phải được triển khai một cách rõ ràng và có thể giải thích được.
- Câu trả lời phải được dựa trên nền tảng dữ liệu có cấu trúc.
- Hệ thống phải tham chiếu đến mệnh đề gốc.

### 3.3 Lựa chọn 2: Chatbot kết hợp Truy xuất (Retrieval-

### Augmented Generation - RAG)

#### 3.3.1 Mục tiêu

Sinh viên phải triển khai một hệ thống Tạo văn bản Kết hợp Truy xuất (RAG) tích hợp:

- Một cơ sở dữ liệu vector được xây dựng từ các mệnh đề hợp đồng.
- Một mô hình phục vụ cho tìm kiếm ngữ nghĩa.
- Một mô hình ngôn ngữ lớn (LLM) để tạo câu trả lời.

Chatbot phải truy xuất các mệnh đề có liên quan trước khi tạo ra một câu trả lời.

#### 3.3.2 Ví dụ

**Input:**

Điều gì xảy ra nếu Bên B chậm trễ thanh toán?

**Output:**

Nếu Bên B chậm trễ thanh toán, mức phạt 1% mỗi ngày sẽ được áp dụng.
(Source: ...)


#### 3.3.3 Yêu cầu

- Hệ thống phải truy xuất k mệnh đề có liên quan nhất.
- Câu trả lời được tạo ra phải bao gồm trích dẫn rõ ràng.
- Hệ thống không được phép ”ảo giác”


