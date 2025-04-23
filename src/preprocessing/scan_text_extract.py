from PIL import Image
import pytesseract
import cv2
import numpy as np
from PIL import Image

# Chemin pour ne pas avoir besoin de toucher le PATH dans les variables d'environnement du système (pas de permission admin)
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\DEOLIVEIRALuana\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"


# OCR: optical character recognition


def preprocess_image(image_path):
    # Charger l'image
    img = cv2.imread(image_path)
    
    # Convertir en niveaux de gris
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Seuillage adaptatif
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)
    
    # Détection des bords
    edges = cv2.Canny(thresh, 50, 150)
    
    return edges

# Utilisation
image_path = r".\docs\examples\img\exemple1_scanned.jpg"
processed_img = preprocess_image(image_path)
# Image.fromarray(processed_img).save("processed.jpg")

def image_to_text(processed_img): 
    """Extrait le texte avec prétraitement"""
    # Prétraitement
    processed_img = preprocess_image(image_path)
    
    # Configuration Tesseract
    custom_config = r'--oem 3 --psm 6 -l fra+eng'
    
    # OCR
    text = pytesseract.image_to_string(
        Image.fromarray(processed_img), 
        config=custom_config
    )
    return text

image_path = r".\docs\examples\img\exemple1_scanned.jpg"
extracted_text = image_to_text(processed_img)
print("Texte extrait :")
print(extracted_text)

