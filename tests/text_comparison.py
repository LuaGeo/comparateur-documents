from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import os
import sys
# Ajoute le chemin racine du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.preprocessing.text_extract import docx_to_text, pdf_to_text

# doc1 = extract_text_from_docx("./docs/examples/doc/exemple1.docx")
# doc2 = extract_text_from_docx("./docs/examples/doc/exemple1_diff.docx")


# Textes bruts à comparer
doc1 = "Fichier PDF d'exemple\nLe Portable Document Format"
doc2 = "Fichier PDF d'exemple2\nLe Portable Document Formatx"

# Vectorisation des textes
vectorizer = CountVectorizer().fit_transform([doc1, doc2])

# Calcul de la similarité cosinus
similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:2])
print(doc1)
print(doc2)
print(f"Similarité : {similarity[0][0]:.2f}")