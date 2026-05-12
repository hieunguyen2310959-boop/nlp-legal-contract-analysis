"""
2.2 SRL — Semantic Role Labeling cho output/clauses.txt
Input : output/clauses.txt + labeled_all.jsonl (fallback: labeled_2_NER.jsonl + labeled_3_NER.jsonl)
Output: output/srl_results.json

Approach: rule-based SRL dùng underthesea word_tokenize + POS tag
  - Predicate : động từ hành động chính của câu
  - Agent     : chủ thể (PARTY entity hoặc NP trước predicate)
  - Theme     : tân ngữ trực tiếp sau predicate
  - Recipient : NP sau "cho/đến/với"
  - Time      : DATE entity hoặc cụm thời gian
  - Condition : mệnh đề điều kiện (nếu/khi/trong trường hợp)
"""

import json
import re
from pathlib import Path

try:
    from underthesea import word_tokenize, pos_tag
    HAS_UNDERSEA = True
except ImportError:
    HAS_UNDERSEA = False
    print("[WARN] underthesea not available, using regex-only fallback.")

# ── Predicate verb patterns (most common legal action verbs) ──────────────────
PREDICATE_PATTERNS = [
    r'phải\s+(\w[\w\s]{1,20}?)(?=\s+(?:cho|đến|về|theo|trong|tại|với|trước|sau|khi|nếu|,|;|\.|$))',
    r'có\s+trách\s+nhiệm\s+(\w[\w\s]{1,20}?)(?=\s+(?:cho|đến|theo|trong|,|;|\.))',
    r'(?:được|có\s+quyền)\s+(\w[\w\s]{1,20}?)(?=\s+(?:cho|đến|theo|trong|,|;|\.))',
    r'không\s+được\s+(\w[\w\s]{1,20}?)(?=\s+(?:cho|đến|theo|trong|,|;|\.))',
    r'bị\s+(phạt\s+\w[\w\s]{0,20}?)(?=\s+(?:tù|tiền|từ|đến|theo|,|;|\.))',
]

# Common predicate verbs in legal text
VERB_LIST = [
    'bàn giao', 'thanh toán', 'trả', 'nộp', 'giao', 'nhận', 'ký kết',
    'thực hiện', 'chấm dứt', 'hủy', 'đình chỉ', 'thu hồi', 'xử phạt',
    'phạt', 'bồi thường', 'khởi kiện', 'giải quyết', 'ban hành',
    'phê duyệt', 'công bố', 'đăng ký', 'báo cáo', 'trao đổi', 'thống nhất',
    'chịu trách nhiệm', 'có trách nhiệm', 'có nghĩa vụ',
    'có quyền', 'được quyền', 'được phép',
    'làm', 'tàng trữ', 'vận chuyển', 'lưu hành', 'sản xuất',
    'kinh doanh', 'mua', 'bán', 'cung ứng', 'đóng',
]

RECIPIENT_PREP = re.compile(r'\b(?:cho|đến|tới|với|giao cho)\s+(.{3,40}?)(?=\s*(?:trong|tại|theo|trước|,|;|\.|\n|$))', re.IGNORECASE)
TIME_PAT = re.compile(
    r'(?:ngày\s+\d{1,2}[/\-]\d{1,2}[/\-]\d{4}'
    r'|ngày\s+\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4}'
    r'|trước\s+ngày\s+\d{1,2}[^\s,;.]{0,20}'
    r'|trong\s+(?:vòng|thời\s+hạn)\s+\d+\s+(?:ngày|tháng|năm)'
    r'|\d+\s+(?:ngày|tháng|năm)\s+kể\s+từ'
    r'|hàng\s+(?:ngày|tháng|năm|tuần|quý)'
    r'|từ\s+\d+\s+(?:năm|tháng|ngày)\s+đến\s+\d+\s+(?:năm|tháng|ngày)(?!\s*(?:đồng|VNĐ|tù)))',
    re.IGNORECASE
)
CONDITION_PAT = re.compile(
    r'(?:nếu|khi|trong\s+trường\s+hợp|trừ\s+trường\s+hợp|trừ\s+khi)\s+.{5,}',
    re.IGNORECASE
)


def find_predicate_simple(text):
    """Find the main predicate verb in a clause."""
    t_lower = text.lower()
    # Check for modal + verb constructs first
    for pat in PREDICATE_PATTERNS:
        m = re.search(pat, t_lower)
        if m:
            return m.group(1).strip()

    # Fallback: find known verb (use word-boundary to avoid partial matches like 'hủy' in 'thủy')
    for verb in VERB_LIST:
        pattern = r'(?<![\w])' + re.escape(verb) + r'(?![\w])'
        if re.search(pattern, t_lower):
            return verb
    return None


def find_agent(text, ner_entities):
    """Agent: PARTY entity, or NP before the predicate."""
    # Prefer explicit PARTY entities
    parties = [e['text'] for e in ner_entities if e.get('label') == 'PARTY']
    if parties:
        return parties[0]

    # Heuristic: first NP (capitalized phrase at start)
    m = re.match(r'^([A-ZÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ][^\s,;.()]{1,40}?)(?=\s+(?:phải|được|có|không|bị|sẽ|đã|đang))',
                text)
    if m:
        return m.group(1).strip()
    return None


def find_theme(text, predicate):
    """Theme: NP immediately after the predicate."""
    if not predicate:
        return None
    idx = text.lower().find(predicate.lower())
    if idx == -1:
        return None
    after = text[idx + len(predicate):].strip()
    # Take first meaningful chunk (stop at prepositions/punctuation)
    m = re.match(r'^(.{3,60}?)(?=\s+(?:cho|đến|tới|với|theo|trong|tại|trước|,|;|\.))', after)
    if m:
        return m.group(1).strip()
    # Fallback: take up to 8 words
    words = after.split()[:8]
    candidate = ' '.join(words).rstrip('.,;')
    return candidate if len(candidate) > 3 else None


def find_recipient(text):
    m = RECIPIENT_PREP.search(text)
    return m.group(1).strip() if m else None


def find_time(text, ner_entities):
    dates = [e['text'] for e in ner_entities if e.get('label') == 'DATE']
    if dates:
        return dates[0]
    m = TIME_PAT.search(text)
    return m.group().strip() if m else None


def find_condition(text):
    m = CONDITION_PAT.search(text)
    if m:
        cond = m.group().strip()
        # Truncate at 120 chars
        return cond[:120] + ('...' if len(cond) > 120 else '')
    return None


def is_processable(text):
    """Skip fragment/title lines."""
    t = text.strip()
    if len(t) < 10:
        return False
    # Skip lettered list items: a) b) c)
    if re.match(r'^\s*[a-zđ]\)', t):
        return False
    # Skip bullet-point list items: - ... or + ...
    if re.match(r'^\s*[-+•]\s+', t):
        return False
    if re.search(r'\s+\d+\.\s*$', t):
        return False
    if t.endswith('(nếu') or t.startswith(')'):
        return False
    return True


def build_srl_record(clause, ner_entities):
    predicate = find_predicate_simple(clause)
    if not predicate:
        return None

    roles = {}
    agent = find_agent(clause, ner_entities)
    if agent:
        roles['Agent'] = agent

    theme = find_theme(clause, predicate)
    if theme:
        roles['Theme'] = theme

    recipient = find_recipient(clause)
    if recipient:
        roles['Recipient'] = recipient

    time_val = find_time(clause, ner_entities)
    if time_val:
        roles['Time'] = time_val

    condition = find_condition(clause)
    if condition:
        roles['Condition'] = condition

    return {
        "clause": clause,
        "predicate": predicate,
        "roles": roles,
    }


def resolve_labeled_files():
    new_file = Path("BTL 2/labeled_NER.jsonl")
    if new_file.exists():
        return [new_file]
    merged = Path("labeled_all.jsonl")
    if merged.exists():
        return [merged]
    return [Path("labeled_2_NER.jsonl"), Path("labeled_3_NER.jsonl")]


def load_entity_map(paths):
    entity_map = {}
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            entity_map[record['text']] = record.get('entities', [])
    return entity_map


def main():
    clauses_path = Path("output/clauses.txt")
    out_path = Path("output/srl_results.json")
    out_path.parent.mkdir(exist_ok=True)

    # Load all clauses
    all_clauses = [l.strip() for l in clauses_path.read_text(encoding='utf-8').splitlines() if l.strip()]
    print(f"Loaded {len(all_clauses)} clauses.")

    labeled_paths = resolve_labeled_files()
    entity_map = load_entity_map(labeled_paths)
    print(f"Using labeled files: {[str(path) for path in labeled_paths if path.exists()]}")
    print(f"Entity hints loaded for {len(entity_map)} clauses.")

    results = []
    skipped = 0
    processed = 0

    for clause in all_clauses:
        if not is_processable(clause):
            skipped += 1
            continue

        ner_entities = entity_map.get(clause, [])
        record = build_srl_record(clause, ner_entities)
        if record:
            results.append(record)
            processed += 1
        else:
            skipped += 1

    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"\nSRL done.")
    print(f"  Processed : {processed}")
    print(f"  Skipped   : {skipped}")
    print(f"  Output    : {out_path}  ({len(results)} records)")

    # ── Sample output ────────────────────────────────────────────────────────
    print("\n── 5 sample records ─────────────────────────────────────────────")
    for r in results[:5]:
        print(f"  Clause   : {r['clause'][:80]}")
        print(f"  Predicate: {r['predicate']}")
        for role, val in r['roles'].items():
            if role != 'Predicate':
                print(f"  {role:<12}: {val[:70]}")
        print()


if __name__ == "__main__":
    main()
