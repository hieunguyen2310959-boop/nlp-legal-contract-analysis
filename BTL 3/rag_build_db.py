"""
BTL 3.3 — Bước 1: Xây dựng Vector Database
==========================================
Chạy file này 1 lần duy nhất để tạo ChromaDB từ clauses.txt.
Sau khi chạy xong, thư mục chroma_db/ sẽ được tạo ra.

Cách chạy:
    python rag_build_db.py
"""

import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
import chromadb


# ── Cấu hình ─────────────────────────────────────────────────────────────────

CLAUSES_PATH     = Path("../output/clauses.txt")
INTENT_PATH      = Path("../output/intent_classification.txt")
SRL_PATH         = Path("../output/srl_results.json")
CHROMA_DB_PATH   = "./chroma_db"
COLLECTION_NAME  = "legal_clauses"

# Embedding model (multilingual, nhẹ, hỗ trợ tiếng Việt)
EMBEDDING_MODEL  = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


# ── Hàm load dữ liệu ─────────────────────────────────────────────────────────

def load_clauses(path: Path) -> list[str]:
    """
    Đọc tất cả mệnh đề từ clauses.txt.
    Mỗi dòng không rỗng là 1 mệnh đề.

    Returns:
        list[str]: danh sách các mệnh đề
    """
    text = path.read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip()]


def load_intent_map(path: Path) -> dict[str, str]:
    """
    Đọc file intent_classification.txt, tạo dict: {mệnh đề -> nhãn intent}.
    Format mỗi dòng: <mệnh đề> ||| <nhãn>

    Returns:
        dict[str, str]: mapping mệnh đề → intent
    """
    intent_map = {}
    text = path.read_text(encoding="utf-8")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            continue
        if not line or "|||" not in line:
            continue

        clause, label = line.rsplit("|||", 1)
        clause = clause.strip()
        label = label.strip()
        if clause and label:
            intent_map[clause] = label
    return intent_map


def load_srl_map(path: Path) -> dict[str, dict]:
    """
    Đọc srl_results.json, tạo dict: {mệnh đề -> roles}.

    Returns:
        dict[str, dict]: mapping mệnh đề → {"Agent": ..., "Theme": ..., ...}
    """
    srl_map = {}
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    for record in data:
        clause = record.get("clause", "")
        roles = dict(record.get("roles", {}))
        if record.get("predicate"):
            roles["predicate"] = record["predicate"]
        if clause:
            srl_map[clause] = roles
    return srl_map


# ── Hàm xây vector database ──────────────────────────────────────────────────

def build_database(
    clauses: list[str],
    intent_map: dict[str, str],
    srl_map: dict[str, dict],
) -> None:
    """
    Embed tất cả mệnh đề và lưu vào ChromaDB.

    Mỗi document trong ChromaDB có:
        - id       : f"clause_{i}"
        - document : nội dung mệnh đề
        - embedding: vector từ SentenceTransformer
        - metadata : {"line", "intent", "agent", "predicate", ...}
    """
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    existing_collections = {collection.name for collection in client.list_collections()}
    if COLLECTION_NAME in existing_collections:
        client.delete_collection(name=COLLECTION_NAME)

    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    embeddings = model.encode(clauses, show_progress_bar=True)
    ids = []
    metadatas = []
    for i, clause in enumerate(clauses):
        ids.append(f"clause_{i}")
        
        metadata = {
            "line": i + 1,
            "intent": intent_map.get(clause, ""),
        }
        
        if clause in srl_map:
            roles = srl_map[clause]
            metadata["agent"] = roles.get("Agent", "")
            metadata["theme"] = roles.get("Theme", "")
            metadata["predicate"] = roles.get("predicate", "")
            metadata["recipient"] = roles.get("Recipient", "")
            metadata["time"] = roles.get("Time", "")
            metadata["condition"] = roles.get("Condition", "")
        
        metadatas.append(metadata)

    collection.add(
        ids=ids,
        documents=clauses,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Đang tải dữ liệu...")
    clauses    = load_clauses(CLAUSES_PATH)
    intent_map = load_intent_map(INTENT_PATH)
    srl_map    = load_srl_map(SRL_PATH)

    print(f"Số mệnh đề: {len(clauses)}")
    print(f"Số intent labels: {len(intent_map)}")
    print(f"Số SRL records: {len(srl_map)}")

    print("\nĐang xây vector database...")
    build_database(clauses, intent_map, srl_map)

    print(f"\nHoàn thành! Database lưu tại: {CHROMA_DB_PATH}/")


if __name__ == "__main__":
    main()
