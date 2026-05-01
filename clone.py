import pandas as pd
from pathlib import Path

df = pd.read_csv("hf://datasets/YuITC/vietnam-legal-documents/raw/train.csv")
output_path = Path(__file__).with_name("vietnam_legal_documents_train_local.csv")
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"Saved to {output_path.resolve()}")