import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from underthesea import dependency_parse


def read_clauses(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Khong tim thay file dau vao: {path}")
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line]


def _parse_row(row: Any) -> Optional[Tuple[int, str, int, str]]:
    # Ho tro nhieu kieu output tu underthesea:
    # 1) tuple/list: (id, token, head, dep) hoac (token, pos, head, dep)
    # 2) dict: {"id":..., "token":..., "head":..., "dep":...}
    if isinstance(row, dict):
        token = row.get("token") or row.get("word") or row.get("form")
        head = row.get("head")
        dep = row.get("dep") or row.get("deprel") or row.get("relation")
        idx = row.get("id")
        if token is None or head is None or dep is None:
            return None
        return int(idx) if idx is not None else -1, str(token), int(head), str(dep)

    if isinstance(row, (tuple, list)):
        if len(row) == 3:
            # Din h dang pho bien: (token, head, dep)
            return -1, str(row[0]), int(row[1]), str(row[2])
        if len(row) >= 4 and isinstance(row[0], int):
            return int(row[0]), str(row[1]), int(row[2]), str(row[3])
        if len(row) >= 4 and isinstance(row[0], str):
            # fallback khi id khong co san
            return -1, str(row[0]), int(row[2]), str(row[3])
    return None


def parse_clause_dependency(clause: str) -> List[Dict[str, Any]]:
    raw = dependency_parse(clause)
    tokens: List[Dict[str, Any]] = []
    auto_id = 1

    for row in raw:
        parsed = _parse_row(row)
        if parsed is None:
            continue
        idx, token, head, dep = parsed
        if idx <= 0:
            idx = auto_id
        tokens.append(
            {
                "id": idx,
                "token": token,
                "head": head,
                "dep": dep,
            }
        )
        auto_id = max(auto_id + 1, idx + 1)

    # Sap xep theo id de output on dinh
    tokens.sort(key=lambda x: x["id"])
    return tokens


def build_dependency_output(clauses: List[str]) -> List[Dict[str, Any]]:
    results = []
    for clause in clauses:
        results.append(
            {
                "clause": clause,
                "tokens": parse_clause_dependency(clause),
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Task 1.3 - Dependency Analysis")
    parser.add_argument(
        "--input",
        default="output/clauses.txt",
        help="Duong dan file clauses dau vao",
    )
    parser.add_argument(
        "--output",
        default="output/dependency.json",
        help="Duong dan file dependency dau ra",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    clauses = read_clauses(input_path)
    data = build_dependency_output(clauses)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Da tao {output_path} voi {len(clauses)} menh de.")


if __name__ == "__main__":
    main()
