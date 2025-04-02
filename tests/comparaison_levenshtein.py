from Levenshtein import distance
from text_extract import docx_to_text, pdf_to_text


# Textes à comparer
doc1 = pdf_to_text(".\docs\pdf\exemple1.pdf")
doc2 = pdf_to_text(".\docs\pdf\exemple1_diff.pdf")

# Calcul de la distance de Levenshtein
lev_distance = distance(doc1, doc2)

# Calcul de la similarité (normalisée entre 0 et 1)
max_length = max(len(doc1), len(doc2))
similarity = 1 - (lev_distance / max_length)

print(f"Distance de Levenshtein : {lev_distance}")
print(f"Similarité : {similarity:.2f}")