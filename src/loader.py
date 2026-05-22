import json
import csv
import io
import yaml
from pypdf import PdfReader


def load_pdf(file) -> str:
    print(f"Loading PDF: {getattr(file, 'name', file)}")
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    print("PDF loading completed")
    return text


def load_txt(file) -> str:
    print(f"Loading TXT/MD: {file.name}")
    text = file.read().decode("utf-8")
    print("TXT loading completed")
    return text


def load_json(file) -> str:
    print(f"Loading JSON: {file.name}")
    data = json.load(file)
    text = json.dumps(data, indent=2)
    print("JSON loading completed")
    return text


def load_yaml(file) -> str:
    print(f"Loading YAML: {file.name}")
    data = yaml.safe_load(file)
    text = yaml.dump(data, default_flow_style=False)
    print("YAML loading completed")
    return text


def load_csv(file) -> str:
    print(f"Loading CSV: {file.name}")
    content = file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    lines = [
        ", ".join(f"{k}: {v}" for k, v in row.items())
        for row in reader
    ]
    text = "\n".join(lines)
    print("CSV loading completed")
    return text


# Supported types and their loaders
LOADERS = {
    ".pdf":  load_pdf,
    ".txt":  load_txt,
    ".md":   load_txt,
    ".json": load_json,
    ".yaml": load_yaml,
    ".yml":  load_yaml,
    ".csv":  load_csv,
}


def load_document(file) -> str:
    """Dispatch to the right loader based on file extension."""
    ext = "." + file.name.lower().rsplit(".", 1)[-1]

    if ext not in LOADERS:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Supported types: {', '.join(LOADERS.keys())}"
        )

    return LOADERS[ext](file)