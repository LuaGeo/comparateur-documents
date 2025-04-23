import pytesseract
from PIL import Image
import cv2
import numpy as np
from Levenshtein import distance
import os
import sys

# Configuration du chemin Tesseract (à adapter)
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'  # Mac/Linux
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\DEOLIVEIRALuana\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'  # Windows

# Ajout du chemin racine
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def preprocess_image_for_ocr(image_path):
    """Améliore la qualité de l'image pour l'OCR"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Dénosage et amélioration du contraste
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    # Binarisation
    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text_with_tesseract(image_path):
    """Extrait le texte avec Tesseract OCR"""
    try:
        print(f"Tentative d'extraction du texte de: {image_path}")
        # Prétraitement
        processed_img = preprocess_image_for_ocr(image_path)
        print("Image prétraitée avec succès")
        
        # Configuration OCR optimisée
        custom_config = r'--oem 3 --psm 6 -l fra+eng'
        
        # Extraction
        text = pytesseract.image_to_string(
            Image.fromarray(processed_img), 
            config=custom_config
        )
        print(f"Texte extrait (longueur: {len(text)})")
        return text.strip()
    except Exception as e:
        print(f"Erreur OCR sur {image_path}: {str(e)}")
        return ""

def compare_documents(doc1_path, doc2_path, is_image=False):
    """Compare deux documents (PDF ou images)"""
    print(f"Comparaison des documents: {doc1_path} et {doc2_path}")
    if is_image:
        text1 = extract_text_with_tesseract(doc1_path)
        text2 = extract_text_with_tesseract(doc2_path)
    else:
        from src.preprocessing.text_extract import pdf_to_text
        text1 = pdf_to_text(doc1_path)
        text2 = pdf_to_text(doc2_path)
    
    print(f"Texte 1 (longueur): {len(text1)}")
    print(f"Texte 2 (longueur): {len(text2)}")
    
    if not text1 or not text2:
        raise ValueError(f"Un des documents n'a pas pu être lu. Texte1 vide: {not text1}, Texte2 vide: {not text2}")
    
    print(text2)

    
    # Calcul de similarité
    lev_distance = distance(text1, text2)
    max_len = max(len(text1), len(text2))
    similarity = 1 - (lev_distance / max_len) if max_len > 0 else 0
    
    return {
        'distance': lev_distance,
        'similarity': similarity,
        'text1_length': len(text1),
        'text2_length': len(text2)
    }

# Exemple d'utilisation
if __name__ == "__main__":
    # Pour les images scannées
    result = compare_documents(
        "./docs/examples/img/exemple1_scanned.jpg",
        "./docs/examples/img/exemple1_diff_scanned.jpg",
        is_image=True
    )
    
    # Pour les PDF texte
    # result = compare_documents("./docs/examples/exemple1.pdf", "./docs/examples/exemple1_diff.pdf")
    
    print(f"Distance de Levenshtein : {result['distance']}")
    print(f"Similarité : {result['similarity']:.2%}")
    print(f"Longueur texte 1 : {result['text1_length']} caractères")
    print(f"Longueur texte 2 : {result['text2_length']} caractères")
