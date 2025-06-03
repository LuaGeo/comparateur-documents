import fitz  # PyMuPDF
import pandas as pd

# Charger un document PDF d'exemple
# Remplace par le chemin réel vers ton fichier
pdf_path = "./docs/examples/pdf/NI 2024 actifs SAVENCIA TRANSPORT VF.pdf"

# Extraction des données
doc = fitz.open(pdf_path)
data = []

for page_num, page in enumerate(doc):
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not text:
                    continue
                data.append({
                    "text": text,
                    "size": span["size"]
                })

# Créer DataFrame
df = pd.DataFrame(data)

# Répartition des tailles de texte : taille + nombre d'occurrences
distribution = df.groupby("size").size().reset_index(name="count").sort_values(by="size", ascending=False)

import ace_tools as tools; tools.display_dataframe_to_user(name="Distribution des tailles de texte", dataframe=distribution)
