import json
import subprocess
import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans
from sklearn.model_selection import train_test_split
from pathlib import Path

PATHS = {
    "input": "output/labeled_NER.jsonl",
    "train_spacy": "train.spacy",
    "dev_spacy": "dev.spacy",
    "base_config": "base_config.cfg",
    "config": "config.cfg",
    "model_dir": "./model",
    "model_best": "./model/model-best",
    "raw_clauses": "output/clauses.txt",
    "output_results": "output/ner_results.json"
}

def parse_to_docbin(data_list, output_path):
    nlp = spacy.blank("vi")
    doc_bin = DocBin()
    
    for data in data_list:
        text = data['text']
        entities = data.get('entities', [])
        
        doc = nlp.make_doc(text)
        spans = []
        for ent in entities:
            start = ent['start']
            end = ent['end']
            label = ent['label']
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is not None:
                spans.append(span)
        
        doc.ents = filter_spans(spans)
        doc_bin.add(doc)
        
    doc_bin.to_disk(output_path)

def prepare_data():
    input_path = Path(PATHS["input"])
    if not input_path.exists():
        raise FileNotFoundError(f"Cannot find input data: {input_path}")
        
    all_data = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            all_data.append(json.loads(line))
            
    # Split train/dev (80/20)
    train_data, dev_data = train_test_split(all_data, test_size=0.2, random_state=42)
    
    parse_to_docbin(train_data, PATHS["train_spacy"])
    parse_to_docbin(dev_data, PATHS["dev_spacy"])
    print(f"Data prepared: {len(train_data)} train samples, {len(dev_data)} dev samples.")

def train_spacy_model():
    print("Preparing data...")
    prepare_data()
    
    # Check if base config exists
    if not Path(PATHS["base_config"]).exists():
        raise FileNotFoundError(f"Missing {PATHS['base_config']}. Please create it before training.")
        
    print("Initializing config...")
    try:
        subprocess.run(
            ["python", "-m", "spacy", "init", "fill-config", PATHS["base_config"], PATHS["config"]],
            check=True, capture_output=True
        )
        
        print("Training model...")
        subprocess.run(
            ["python", "-m", "spacy", "train", PATHS["config"], "--output", PATHS["model_dir"], 
             "--paths.train", PATHS["train_spacy"], "--paths.dev", PATHS["dev_spacy"]],
            check=True
        )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        raise RuntimeError(f"SpaCy command failed:\n{error_msg}")

def predict():
    print("Loading model and predicting...")
    model_path = Path(PATHS["model_best"])
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}. Please train the model first.")
        
    clauses_path = Path(PATHS["raw_clauses"])
    if not clauses_path.exists():
        raise FileNotFoundError(f"Raw clauses not found at {clauses_path}.")
        
    nlp = spacy.load(model_path)
    results = []
    
    with open(clauses_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            text = line.strip()
            if not text:
                continue
            
            doc = nlp(text)
            entities = [{
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            } for ent in doc.ents]
            
            results.append({
                "clause_id": i + 1,
                "text": text,
                "entities": entities
            })
            
    with open(PATHS["output_results"], "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
    print(f"Saved results to {PATHS['output_results']}")

if __name__ == "__main__":
    train_spacy_model()
    predict()
