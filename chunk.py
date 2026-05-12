import argparse
from pathlib import Path
from typing import List, Tuple

from underthesea import pos_tag, word_tokenize


def read_clauses(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Khong tim thay file dau vao: {path}")
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line]


def is_np_pos(pos: str) -> bool:
    # Tap nhan danh tu/so tu/loai tu pho bien trong bo POS tieng Viet
    return pos in {"N", "Np", "Nc", "Nu", "M", "L", "Ny", "X"}


def is_legal_np_token(token: str) -> bool:
    t = token.strip()
    if not t:
        return False
    if t[0].isupper() and any(ch.isalpha() for ch in t):
        return True
    if any(ch.isdigit() for ch in t):
        return True
    if any(ch in t for ch in {"/", "-"}):
        return True
    return False


def chunk_clause_iob(clause: str) -> List[Tuple[str, str]]:
    # word_tokenize tra ve chuoi co dau gach duoi cho multi-syllable token
    tokenized = word_tokenize(clause, format="text")
    pos_pairs = pos_tag(tokenized)

    result: List[Tuple[str, str]] = []
    inside_np = False
    prev_token = ""
    for token, pos in pos_pairs:
        token_norm = token.strip()
        prev_norm = prev_token.strip().lower()

        force_np = False
        if token_norm.lower() in {"bên", "điều", "khoản", "mục", "nghị", "thông", "quyết", "luật"}:
            force_np = True
        if prev_norm in {"bên", "điều", "khoản", "mục"} and is_legal_np_token(token_norm):
            force_np = True
        if is_legal_np_token(token_norm):
            force_np = True

        if is_np_pos(pos) or force_np:
            label = "I-NP" if inside_np else "B-NP"
            inside_np = True
        else:
            label = "O"
            inside_np = False

        result.append((token, label))
        prev_token = token

    return result


def write_chunks(chunks: List[List[Tuple[str, str]]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for clause_chunks in chunks:
            for token, label in clause_chunks:
                f.write(f"{token} {label}\n")
            f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Task 1.2 - Noun Phrase Chunking (IOB)")
    parser.add_argument(
        "--input",
        default="output/clauses.txt",
        help="Duong dan file clauses dau vao",
    )
    parser.add_argument(
        "--output",
        default="output/chunks.txt",
        help="Duong dan file chunks dau ra",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    clauses = read_clauses(input_path)
    all_chunks = [chunk_clause_iob(clause) for clause in clauses]
    write_chunks(all_chunks, output_path)

    print(f"Da tao {output_path} voi {len(clauses)} menh de.")


if __name__ == "__main__":
    main()
