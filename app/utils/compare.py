from Levenshtein import distance
import PyPDF2
from docx import Document

def highlight_differences(text1, text2):
    """Génère un HTML avec surlignage des différences"""
    from difflib import HtmlDiff
    return HtmlDiff().make_file(
        text1.splitlines(), 
        text2.splitlines(),
        fromdesc="Document 1",
        todesc="Document 2"
    )

def compare_documents(doc1, doc2):
    # ... (votre code existant)
    return {
        'distance': lev_distance,
        'similarity': similarity,
        'text1': text1,
        'text2': text2,
        'text1_length': len(text1),
        'text2_length': len(text2)
    }