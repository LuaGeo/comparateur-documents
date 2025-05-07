from PIL import Image
import pytesseract
import cv2
import numpy as np
import platform
import os

def configure_tesseract_path():
    """Configure le chemin de Tesseract en fonction du système d'exploitation"""
    system = platform.system()
    
    # Chemins possibles pour Windows
    windows_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Users\DEOLIVEIRALuana\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    ]
    
    # Chemins possibles pour Mac/Linux
    unix_paths = [
        '/usr/local/bin/tesseract',
        '/usr/bin/tesseract',
        '/opt/homebrew/bin/tesseract'  # Pour Mac avec Homebrew
    ]
    
    if system == 'Windows':
        for path in windows_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return
    else:  # Mac ou Linux
        for path in unix_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return
    
    raise EnvironmentError("Tesseract non trouvé. Veuillez l'installer et vérifier les chemins.")

# Configurer le chemin de Tesseract
configure_tesseract_path()

# OCR: optical character recognition


def preprocess_image(image_path):
    """Prétraite l'image pour améliorer la reconnaissance de texte"""
    try:
        # Charger l'image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Impossible de charger l'image: {image_path}")
        
        # Convertir en niveaux de gris
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Ajustement simple du contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Binarisation simple
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    except Exception as e:
        print(f"Erreur lors du prétraitement de l'image: {str(e)}")
        raise

def image_to_text(image_path):
    """Extrait le texte d'une image avec prétraitement"""
    try:
        print(f"Tentative d'extraction du texte de: {image_path}")
        
        # Vérifier si le fichier existe
        if not os.path.exists(image_path):
            raise ValueError(f"Le fichier n'existe pas: {image_path}")
        
        # Prétraitement
        processed_img = preprocess_image(image_path)
        print("Image prétraitée avec succès")
        
        # Configuration Tesseract optimisée pour texte clair
        custom_config = '--oem 3 --psm 6 -l fra+eng --dpi 300'
        
        # OCR
        text = pytesseract.image_to_string(
            Image.fromarray(processed_img), 
            config=custom_config
        )
        
        print(f"Texte extrait (longueur: {len(text)}): {text[:100]}...")
        return text.strip()
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte: {str(e)}")
        return ""

